"""Pydantic models for structured quiz output."""

from pydantic import BaseModel, Field


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
