"""Quiz generation module using LangChain + OpenAI."""

import logging

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.quiz.models import DocumentPreview, Quiz, Question, QuizInputs, QuizPlan

logger = logging.getLogger(__name__)

DEFAULT_QUIZ_TITLE = "Document Quiz"
EXCERPT_MAX_CHARS = 500

SYSTEM_PROMPT = """\
You are an expert quiz maker. Given the content extracted from a PDF document, \
generate a high-quality, challenging multiple-choice quiz that tests deep understanding.

Rules:
1. Each question MUST have exactly 4 options labeled A, B, C, D.
2. Exactly ONE option must be the correct answer.
3. Provide a clear, concise explanation for why the correct answer is right.
4. Include the source page number from the document for each question.
5. Questions should test conceptual understanding and critical thinking, not just trivial facts.
6. INCORRECT OPTIONS (DISTRACTORS) MUST BE HIGHLY PLAUSIBLE AND LOGICAL.
   - Do NOT use obviously wrong, silly, or throwaway options.
   - Use common misconceptions or partially correct statements as distractors.
   - It should require genuine knowledge of the content to eliminate the wrong choices.
7. Cover different sections/topics of the document for a comprehensive quiz.
8. NEVER repeat or duplicate a question — every question must test a unique concept.
9. Within each question, all 4 options MUST be meaningfully different from each other.
10. Do NOT reuse the same correct answer text across multiple questions.
"""

SYSTEM_RULES: list[str] = [
    "Each question has exactly 4 options labeled A, B, C, D.",
    "Exactly one option is correct, with a clear explanation.",
    "Distractors must be plausible — no throwaway options.",
    "Each question cites the source page number from the PDF.",
    "No duplicate questions; all 4 options must be meaningfully different.",
    "Do not reuse the same correct-answer text across questions.",
]


def _build_context(documents: list[Document]) -> str:
    """Combine document chunks into a single context string with page references."""
    parts: list[str] = []
    for doc in documents:
        page = doc.metadata.get("page", "unknown")
        parts.append(f"[Page {page}]\n{doc.page_content}")
    return "\n\n".join(parts)


def build_document_preview(documents: list[Document], filename: str) -> DocumentPreview:
    """Summarize ingested chunks for the preview response.

    `pages` is the count of unique pages with extracted text. Chunks missing
    a `page` metadata key (or with `page=None`) are excluded. `excerpt` is
    the first EXCERPT_MAX_CHARS of the joined context, which begins at the
    first chunk's `[Page N]` header.
    """
    pages = {
        d.metadata.get("page") for d in documents if d.metadata.get("page") is not None
    }
    excerpt = _build_context(documents)[:EXCERPT_MAX_CHARS]
    return DocumentPreview(filename=filename, pages=len(pages), excerpt=excerpt)


def _normalize(text: str) -> str:
    """Lowercase, strip, and collapse whitespace for comparison."""
    return " ".join(text.lower().split())


def _build_user_prompt_text(inputs: QuizInputs, context: str) -> str:
    """Render the human-side prompt as plain text. Optional fields render only when set."""
    title = inputs.quiz_name.strip() or DEFAULT_QUIZ_TITLE
    lines: list[str] = [
        f'Generate a quiz titled "{title}" with {inputs.num_questions} multiple-choice '
        f"questions based on the provided document content.",
        "",
        "IMPORTANT: Every question must be unique — do not repeat or rephrase any "
        "question. Each question's 4 options must all be distinct from each other.",
    ]

    optional: list[tuple[str, str]] = [
        ("Focus topics", inputs.focus_topics),
        ("Difficulty", inputs.difficulty or ""),
        ("Question style", inputs.question_style),
        ("Extra instructions", inputs.extra_instructions),
    ]
    rendered_optional = [f"{label}: {value}" for label, value in optional if value]
    if rendered_optional:
        lines.append("")
        lines.extend(rendered_optional)

    lines += [
        "",
        "--- DOCUMENT CONTENT ---",
        context,
        "--- END DOCUMENT CONTENT ---",
        "",
        "Generate the quiz now.",
    ]
    return "\n".join(lines)


def _deduplicate_quiz(quiz: Quiz) -> Quiz:
    """
    Remove duplicate questions and fix within-question option duplicates.

    Two checks:
    1. Cross-question: drop questions whose text is a duplicate of an earlier one.
    2. Within-question: if any two options share identical text, flag and drop
       the question (since we can't invent a replacement option).
    """
    seen_questions: set[str] = set()
    unique: list[Question] = []
    dropped = 0

    for q in quiz.questions:
        norm_q = _normalize(q.question)

        # Check 1: duplicate question text
        if norm_q in seen_questions:
            dropped += 1
            continue

        # Check 2: duplicate options within the same question
        option_texts = [_normalize(opt.text) for opt in q.options]
        if len(option_texts) != len(set(option_texts)):
            dropped += 1
            continue

        seen_questions.add(norm_q)
        unique.append(q)

    if dropped:
        logger.warning(f"Removed {dropped} duplicate/invalid question(s)")

    quiz.questions = unique
    return quiz


def build_plan(inputs: QuizInputs, document: DocumentPreview, context: str) -> QuizPlan:
    """Render a structured plan from validated inputs + a document preview.

    Pure function — no I/O. Called by the /preview-prompt route after the PDF
    has been ingested into chunks.
    """
    prompt = _build_user_prompt_text(inputs, context)
    return QuizPlan(
        document=document,
        prompt=prompt,
    )


def generate_quiz(prompt: str, model: str) -> Quiz:
    """Generate a structured MCQ quiz using a pre-generated prompt."""
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]

    llm = ChatOpenAI(model=model, temperature=0.3)
    structured_llm = llm.with_structured_output(Quiz)

    logger.info(f"Generating quiz using {model}...")
    quiz: Quiz = structured_llm.invoke(messages)

    quiz = _deduplicate_quiz(quiz)

    logger.info(f"Generated quiz: '{quiz.title}' with {len(quiz.questions)} questions")
    return quiz
