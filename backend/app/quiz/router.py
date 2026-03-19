"""Quiz generation API router."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.quiz.ingest import ingest_pdf
from app.quiz.generator import generate_quiz

router = APIRouter()

_ALLOWED_MODELS = {"gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"}
_MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/generate")
async def generate(
    pdf: UploadFile = File(...),
    num_questions: int = Form(default=10, ge=1, le=50),
    model: str = Form(default="gpt-4o-mini"),
    quiz_name: str = Form(default=""),
):
    """
    Upload a PDF and generate an MCQ quiz.

    Returns the structured quiz as JSON.
    """
    if not pdf.filename or not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    if model not in _ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model}' is not allowed. Choose from: {sorted(_ALLOWED_MODELS)}",
        )

    content = await pdf.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")

    if len(content) > _MAX_PDF_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds the 20 MB size limit.",
        )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        documents = ingest_pdf(tmp_path)
        quiz = generate_quiz(
            documents,
            num_questions=num_questions,
            model=model,
            quiz_name=quiz_name,
        )
        if not quiz.questions:
            raise HTTPException(
                status_code=422,
                detail="Quiz generation produced no valid questions. Try a different PDF or fewer questions.",
            )
        return quiz.model_dump()
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Quiz generation failed. Please try again.")
    finally:
        tmp_path.unlink(missing_ok=True)
