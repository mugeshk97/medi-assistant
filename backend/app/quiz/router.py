"""Quiz generation API router."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.quiz.ingest import ingest_pdf
from app.quiz.generator import generate_quiz

router = APIRouter()


@router.post("/generate")
async def generate(
    pdf: UploadFile = File(...),
    num_questions: int = Form(default=10),
    model: str = Form(default="gpt-4o-mini"),
    quiz_name: str = Form(default=""),
):
    """
    Upload a PDF and generate an MCQ quiz.

    Returns the structured quiz as JSON.
    """
    if not pdf.filename or not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await pdf.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")
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
        return quiz.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)
