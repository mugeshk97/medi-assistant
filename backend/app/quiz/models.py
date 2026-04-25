"""Pydantic models for structured quiz output."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class Option(BaseModel):
    """A single option for a multiple-choice question."""

    label: str = Field(description="Option label, e.g. 'A', 'B', 'C', 'D'")
    text: str = Field(description="The option text")


class Question(BaseModel):
    """A single multiple-choice question generated from the document."""

    question: str = Field(description="The question text")
    options: list[Option] = Field(
        description="Exactly 4 options labeled A through D", min_length=4, max_length=4
    )
    correct_answer: str = Field(
        description="The label of the correct option, e.g. 'A', 'B', 'C', or 'D'"
    )
    explanation: str = Field(
        description="A brief explanation of why the correct answer is right"
    )
    source_page: int = Field(
        description="The page number from the source PDF where this information is found"
    )


class Quiz(BaseModel):
    """A complete quiz generated from a PDF document."""

    title: str = Field(description="A descriptive title for the quiz")
    questions: list[Question] = Field(description="List of MCQ questions")


ALLOWED_MODELS: tuple[str, ...] = (
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
)


class DocumentPreview(BaseModel):
    """Lightweight summary of an ingested PDF, shown in the preview plan.

    `pages` counts unique pages with extractable text — image-only pages
    produce no chunk and are not counted.
    """

    filename: str
    pages: int
    excerpt: str


class QuizInputs(BaseModel):
    """User-editable inputs that feed both the preview and the generate endpoints."""

    quiz_name: str = Field(default="", max_length=200)
    num_questions: int = Field(default=10, ge=1, le=50)
    model: str = Field(default="gpt-4o-mini")
    focus_topics: str = Field(default="", max_length=500)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    question_style: str = Field(default="", max_length=200)
    extra_instructions: str = Field(default="", max_length=1000)

    @field_validator(
        "quiz_name",
        "focus_topics",
        "question_style",
        "extra_instructions",
        mode="before",
    )
    @classmethod
    def _strip_text(cls, v):
        if v is None:
            return ""
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("difficulty", mode="before")
    @classmethod
    def _empty_difficulty_is_none(cls, v):
        if v in ("", None):
            return None
        return v

    @field_validator("model")
    @classmethod
    def _model_in_allowlist(cls, v: str) -> str:
        if v not in ALLOWED_MODELS:
            raise ValueError(
                f"model '{v}' is not allowed; choose one of {list(ALLOWED_MODELS)}"
            )
        return v


class QuizPlan(BaseModel):
    """Structured preview of what the LLM will be asked to do.

    The client renders this as a readable plan; rules are read-only and reflect
    the system prompt's fixed contract.
    """

    title: str
    num_questions: int
    model: str
    focus_topics: str
    difficulty: Optional[Literal["easy", "medium", "hard"]]
    question_style: str
    extra_instructions: str
    document: DocumentPreview
    rules: list[str]
