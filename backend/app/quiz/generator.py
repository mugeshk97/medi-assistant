"""Quiz generation module using LangChain + OpenAI."""

import logging

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.quiz.models import Quiz, Question, QuizInputs, QuizPlan

logger = logging.getLogger(__name__)

DOCUMENT_PLACEHOLDER = "<PDF you upload at generation time will be inserted here>"
DEFAULT_QUIZ_TITLE = "Document Quiz"

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

# NOTE: This placeholder is used by generate_quiz and will be replaced in Task 6.
USER_PROMPT = ""


def _build_context(documents: list[Document]) -> str:
    """Combine document chunks into a single context string with page references."""
    parts: list[str] = []
    for doc in documents:
        page = doc.metadata.get("page", "unknown")
        parts.append(f"[Page {page}]\n{doc.page_content}")
    return "\n\n".join(parts)


def _normalize(text: str) -> str:
    """Lowercase, strip, and collapse whitespace for comparison."""
    return " ".join(text.lower().split())


def _build_user_prompt_text(inputs: QuizInputs, context: str) -> str:
    """Render the human-side prompt as plain text. Optional fields render only when set."""
    title = inputs.quiz_name.strip() or DEFAULT_QUIZ_TITLE
    lines: list[str] = [
        f'Generate a quiz titled "{title}" with {inputs.num_questions} multiple-choice '
        f"questions based on the following document content.",
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
        "Generate the quiz now. Use the exact title provided above.",
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


def build_plan(inputs: QuizInputs) -> QuizPlan:
    """Render a structured plan from validated inputs. Pure function — no I/O."""
    title = inputs.quiz_name.strip() or DEFAULT_QUIZ_TITLE
    return QuizPlan(
        title=title,
        num_questions=inputs.num_questions,
        model=inputs.model,
        focus_topics=inputs.focus_topics,
        difficulty=inputs.difficulty,
        question_style=inputs.question_style,
        extra_instructions=inputs.extra_instructions,
        document_source=DOCUMENT_PLACEHOLDER,
        rules=list(SYSTEM_RULES),
    )


def generate_quiz(
    documents: list[Document],
    num_questions: int = 10,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
    quiz_name: str = "",
) -> Quiz:
    """
    Generate a structured MCQ quiz from document chunks.

    Args:
        documents: List of LangChain Document objects from PDF ingestion.
        num_questions: Number of questions to generate.
        model: OpenAI model name to use.
        temperature: Sampling temperature for generation.
        quiz_name: Optional custom name for the quiz.

    Returns:
        A Quiz object with deduplicated questions.
    """
    context = _build_context(documents)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT),
        ]
    )

    llm = ChatOpenAI(model=model, temperature=temperature)

    # Use structured output to get a validated Quiz object
    structured_llm = llm.with_structured_output(Quiz)

    chain = prompt | structured_llm

    final_name = quiz_name.strip() if quiz_name else "Document Quiz"
    logger.info(f"Generating {num_questions} questions using {model}...")
    quiz = chain.invoke(
        {
            "num_questions": num_questions,
            "context": context,
            "quiz_name": final_name,
        }
    )

    # Override title with user-provided name if given
    if quiz_name.strip():
        quiz.title = quiz_name.strip()

    # Post-generation deduplication safety net
    quiz = _deduplicate_quiz(quiz)

    logger.info(f"Generated quiz: '{quiz.title}' with {len(quiz.questions)} questions")
    return quiz
