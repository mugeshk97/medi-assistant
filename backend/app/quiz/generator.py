"""Quiz generation module using LangChain + OpenAI."""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.quiz.models import Quiz, Question


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

USER_PROMPT = """\
Generate a quiz titled "{quiz_name}" with {num_questions} multiple-choice questions based on the following document content.

IMPORTANT: Every question must be unique — do not repeat or rephrase any question. \
Each question's 4 options must all be distinct from each other.

--- DOCUMENT CONTENT ---
{context}
--- END DOCUMENT CONTENT ---

Generate the quiz now. Use the exact title provided above.
"""


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
        print(f"⚠️  Removed {dropped} duplicate/invalid question(s)")

    quiz.questions = unique
    return quiz


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
    print(f"🤖 Generating {num_questions} questions using {model}...")
    quiz = chain.invoke({
        "num_questions": num_questions,
        "context": context,
        "quiz_name": final_name,
    })

    # Override title with user-provided name if given
    if quiz_name.strip():
        quiz.title = quiz_name.strip()

    # Post-generation deduplication safety net
    quiz = _deduplicate_quiz(quiz)

    print(f"✅ Generated quiz: '{quiz.title}' with {len(quiz.questions)} questions")
    return quiz
