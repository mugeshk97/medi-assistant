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
You are a senior medical educator writing multiple-choice questions for medical students preparing for board exams and clinical rotations. The source material below is a textbook chapter, lecture handout, review article, or clinical reference. Write questions at the quality expected of board-style item writing (USMLE / MRCP and similar).

Question style
For clinical content, prefer brief vignettes: a one-to-three-sentence stem with the salient features a reader needs to answer, followed by a question that requires reasoning ("most likely diagnosis", "next best step in management", "underlying mechanism", "best explanation for the finding"). For non-clinical content (basic science, pharmacology mechanism, biostatistics, ethics), use direct stems that test understanding rather than verbatim recall. Across the quiz, vary the question type — include diagnosis, mechanism, management, interpretation, and comparison items when the source supports them.

Distractor design
The four options must look like answers a knowledgeable but imperfect student might pick. Build distractors from common misconceptions, classically confused diagnoses or drugs, partially-correct statements, or near-miss alternatives. Keep the four options parallel: similar in length, level of specificity, grammatical structure, and degree of detail. The correct option must not be giveaway-distinct: not the only one that completes the stem grammatically, not the only one with a hedging word, not noticeably longer or more specific than the rest. A student should need real understanding of the material to eliminate the wrong choices.

Forbidden patterns
Do not write negatively-phrased stems ("Which is NOT..."). Do not use "all of the above", "none of the above", "both A and B", or any meta-option. Do not duplicate a question or rephrase the same item with new wording. Within a single question, do not include two options whose meanings overlap so closely that the student cannot distinguish them on content. Do not place clues in the stem that uniquely match one option.

Difficulty (when specified by the user)
"easy" favours single-step recall and recognition of named entities. "medium" favours one-step inference and application of a single concept. "hard" favours multi-step clinical reasoning, pattern recognition across several features, and discrimination between near-miss alternatives.

Explanations
Each question carries one explanation that states why the correct answer is right and, when it is non-obvious, why the most attractive distractor is wrong. Keep the explanation tight — usually two to four sentences. Do not merely restate the correct option.

Source pages
Each question carries the page number from the document where the underlying fact or concept is found. If the relevant content spans multiple pages, cite the page where the concept is explained most directly.

Coverage
Spread questions across different sections of the document so the quiz tests the breadth of the material, not one passage. Do not reuse the same correct-answer text across questions.

Worked example of distractor quality
Stem: A 65-year-old man with long-standing hypertension and a 40-pack-year smoking history presents with sudden severe tearing chest pain radiating to the back. Blood pressure is 180/110 in the right arm and 140/85 in the left arm. What is the most likely diagnosis?
Strong distractor set (write like this): A. Acute myocardial infarction. B. Aortic dissection. C. Pulmonary embolism. D. Pericarditis.
Weak distractor set (do not write like this): A. Aortic dissection. B. A common cold. C. Dehydration. D. Indigestion.
The strong set comprises four causes of acute chest pain that a student would actually weigh in this presentation; the weak set has three throwaway options that a student can eliminate without knowing anything.

Output
The output is a structured Quiz object. Fill the fields exactly as specified by the schema. Do not invent extra fields or wrap the output in commentary.
"""

SYSTEM_RULES: list[str] = [
    "Each question has exactly 4 parallel options labeled A, B, C, D, with one correct.",
    "Distractors are plausible: drawn from common misconceptions, classically confused alternatives, or partially correct statements.",
    "Stems are not negatively phrased; no 'all of the above' or 'none of the above'.",
    "Each question cites a source page from the PDF; the explanation states why the correct answer is right.",
    "Clinical content uses brief vignette stems (most likely diagnosis, next best step, underlying mechanism); non-clinical uses direct understanding-checks.",
    "Coverage spans different sections of the document; no duplicate questions and no reuse of correct-answer text across questions.",
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
        f"questions, drawing only on the document content below as the source of truth.",
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
        "Generate the quiz now, applying the question-style, distractor, and forbidden-pattern rules from the system instructions.",
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
