"""Quiz generation API router."""

import json
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.quiz.generator import build_document_preview, build_plan, generate_quiz
from app.quiz.ingest import ingest_pdf
from app.quiz.models import QuizInputs, QuizPlan

router = APIRouter()

_MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB


@asynccontextmanager
async def _accept_pdf_upload(pdf: UploadFile) -> AsyncIterator[Path]:
    """Validate the upload, persist it to a temp file, yield the path, clean up.

    Raises HTTPException with the existing status codes:
      400 — missing or non-".pdf" filename, empty body
      413 — body exceeds _MAX_PDF_BYTES
    """
    if not pdf.filename or not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")

    content = await pdf.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")
    if len(content) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF exceeds the 20 MB size limit.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        yield tmp_path
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/preview-prompt", response_model=QuizPlan)
async def preview_prompt(
    pdf: UploadFile = File(...),
    num_questions: int = Form(default=10),
    model: str = Form(default="gpt-4o-mini"),
    quiz_name: str = Form(default=""),
    focus_topics: str = Form(default=""),
    difficulty: str = Form(default=""),
    question_style: str = Form(default=""),
    extra_instructions: str = Form(default=""),
) -> QuizPlan:
    """Ingest the PDF and return a plan describing what the LLM will be asked to do.

    No LLM call. The client uses this to verify extraction and approve fields
    before paying for /generate.
    """
    try:
        inputs = QuizInputs(
            quiz_name=quiz_name,
            num_questions=num_questions,
            model=model,
            focus_topics=focus_topics,
            difficulty=difficulty,
            question_style=question_style,
            extra_instructions=extra_instructions,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json()))

    async with _accept_pdf_upload(pdf) as tmp_path:
        documents = ingest_pdf(tmp_path)
        if not documents:
            raise HTTPException(
                status_code=422,
                detail="PDF produced no extractable text. Try a different document.",
            )
        document = build_document_preview(documents, pdf.filename or "")
        return build_plan(inputs, document)


@router.post("/generate")
async def generate(
    pdf: UploadFile = File(...),
    num_questions: int = Form(default=10),
    model: str = Form(default="gpt-4o-mini"),
    quiz_name: str = Form(default=""),
    focus_topics: str = Form(default=""),
    difficulty: str = Form(default=""),
    question_style: str = Form(default=""),
    extra_instructions: str = Form(default=""),
):
    """Upload a PDF and generate an MCQ quiz."""
    try:
        inputs = QuizInputs(
            quiz_name=quiz_name,
            num_questions=num_questions,
            model=model,
            focus_topics=focus_topics,
            difficulty=difficulty,
            question_style=question_style,
            extra_instructions=extra_instructions,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json()))

    async with _accept_pdf_upload(pdf) as tmp_path:
        try:
            documents = ingest_pdf(tmp_path)
            quiz = generate_quiz(documents, inputs)
            if not quiz.questions:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Quiz generation produced no valid questions. "
                        "Try a different PDF or fewer questions."
                    ),
                )
            return quiz.model_dump()
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception:
            raise HTTPException(
                status_code=500, detail="Quiz generation failed. Please try again."
            )
