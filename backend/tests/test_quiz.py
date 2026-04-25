"""Tests for quiz inputs, plan, and prompt rendering."""

import pytest
from pydantic import ValidationError

from langchain_core.documents import Document

from app.quiz.generator import (
    SYSTEM_PROMPT,
    SYSTEM_RULES,
    build_plan,
    DOCUMENT_PLACEHOLDER,
    _build_user_prompt_text,
    generate_quiz,
)
from app.quiz.models import (
    DocumentPreview,
    Option,
    Question,
    Quiz,
    QuizInputs,
    QuizPlan,
)


def _api_headers() -> dict:
    """Return headers with API key for authenticated requests."""
    from app.settings import get_settings

    settings = get_settings()
    if settings.API_KEY:
        return {"X-API-Key": settings.API_KEY}
    return {}


class TestQuizInputs:
    def test_defaults(self):
        inputs = QuizInputs()
        assert inputs.quiz_name == ""
        assert inputs.num_questions == 10
        assert inputs.model == "gpt-4o-mini"
        assert inputs.focus_topics == ""
        assert inputs.difficulty is None
        assert inputs.question_style == ""
        assert inputs.extra_instructions == ""

    def test_all_fields_set(self):
        inputs = QuizInputs(
            quiz_name="Cardio Basics",
            num_questions=12,
            model="gpt-4o",
            focus_topics="ECG, arrhythmias",
            difficulty="medium",
            question_style="case scenarios",
            extra_instructions="Avoid trivia.",
        )
        assert inputs.quiz_name == "Cardio Basics"
        assert inputs.difficulty == "medium"

    def test_strips_whitespace(self):
        inputs = QuizInputs(quiz_name="  Cardio  ", focus_topics="  topic  ")
        assert inputs.quiz_name == "Cardio"
        assert inputs.focus_topics == "topic"

    @pytest.mark.parametrize("n", [0, 51, -1])
    def test_num_questions_out_of_range(self, n):
        with pytest.raises(ValidationError):
            QuizInputs(num_questions=n)

    def test_model_not_in_allowlist(self):
        with pytest.raises(ValidationError):
            QuizInputs(model="gpt-5-imagined")

    @pytest.mark.parametrize("d", ["", "EASY", "extreme", "Medium"])
    def test_difficulty_invalid(self, d):
        # Empty string is coerced to None and accepted; everything else is invalid.
        if d == "":
            assert QuizInputs(difficulty=d).difficulty is None
        else:
            with pytest.raises(ValidationError):
                QuizInputs(difficulty=d)

    def test_quiz_name_too_long(self):
        with pytest.raises(ValidationError):
            QuizInputs(quiz_name="x" * 201)

    def test_focus_topics_too_long(self):
        with pytest.raises(ValidationError):
            QuizInputs(focus_topics="x" * 501)

    def test_question_style_too_long(self):
        with pytest.raises(ValidationError):
            QuizInputs(question_style="x" * 201)

    def test_extra_instructions_too_long(self):
        with pytest.raises(ValidationError):
            QuizInputs(extra_instructions="x" * 1001)


class TestQuizPlan:
    def test_construct_full_plan(self):
        plan = QuizPlan(
            title="Cardio Basics",
            num_questions=10,
            model="gpt-4o-mini",
            focus_topics="ECG",
            difficulty="medium",
            question_style="case scenarios",
            extra_instructions="",
            document_source="<placeholder>",
            rules=["rule one", "rule two"],
        )
        assert plan.title == "Cardio Basics"
        assert plan.rules == ["rule one", "rule two"]

    def test_difficulty_optional(self):
        plan = QuizPlan(
            title="Q",
            num_questions=5,
            model="gpt-4o-mini",
            focus_topics="",
            difficulty=None,
            question_style="",
            extra_instructions="",
            document_source="x",
            rules=[],
        )
        assert plan.difficulty is None


class TestDocumentPreview:
    def test_construct(self):
        dp = DocumentPreview(filename="cardio.pdf", pages=3, excerpt="hello")
        assert dp.filename == "cardio.pdf"
        assert dp.pages == 3
        assert dp.excerpt == "hello"

    def test_round_trip(self):
        dp = DocumentPreview(filename="cardio.pdf", pages=3, excerpt="hello")
        assert DocumentPreview.model_validate(dp.model_dump()) == dp


class TestSystemRules:
    def test_rules_non_empty(self):
        assert len(SYSTEM_RULES) >= 5
        for r in SYSTEM_RULES:
            assert isinstance(r, str) and r.strip() == r and len(r) > 0

    def test_each_rule_has_trace_in_system_prompt(self):
        """Every rule must be backed by a numbered line in SYSTEM_PROMPT.

        Catches one-sided edits: if you change a rule in SYSTEM_PROMPT but
        forget SYSTEM_RULES (or vice versa), this fails.
        """
        prompt_lower = SYSTEM_PROMPT.lower()
        rule_keywords = {
            "Each question has exactly 4 options labeled A, B, C, D.": "exactly 4 options",
            "Exactly one option is correct, with a clear explanation.": "exactly one option",
            "Distractors must be plausible — no throwaway options.": "plausible",
            "Each question cites the source page number from the PDF.": "source page",
            "No duplicate questions; all 4 options must be meaningfully different.": "duplicate",
            "Do not reuse the same correct-answer text across questions.": "reuse",
        }
        for r in SYSTEM_RULES:
            assert r in rule_keywords, f"SYSTEM_RULES entry not registered: {r!r}"
            assert rule_keywords[r] in prompt_lower, (
                f"Drift detected: rule {r!r} expects keyword "
                f"{rule_keywords[r]!r} in SYSTEM_PROMPT but it is missing."
            )


class TestBuildPlan:
    def test_full_inputs_round_trip(self):
        inputs = QuizInputs(
            quiz_name="Cardio Basics",
            num_questions=12,
            model="gpt-4o",
            focus_topics="ECG, arrhythmias",
            difficulty="hard",
            question_style="case scenarios",
            extra_instructions="Avoid trivia.",
        )
        plan = build_plan(inputs)
        assert plan.title == "Cardio Basics"
        assert plan.num_questions == 12
        assert plan.model == "gpt-4o"
        assert plan.focus_topics == "ECG, arrhythmias"
        assert plan.difficulty == "hard"
        assert plan.question_style == "case scenarios"
        assert plan.extra_instructions == "Avoid trivia."
        assert plan.document_source == DOCUMENT_PLACEHOLDER
        assert plan.rules == SYSTEM_RULES

    def test_defaults_use_fallback_title(self):
        plan = build_plan(QuizInputs())
        assert plan.title == "Document Quiz"  # fallback when quiz_name is empty
        assert plan.focus_topics == ""
        assert plan.difficulty is None
        assert plan.rules == SYSTEM_RULES

    def test_blank_quiz_name_uses_fallback(self):
        plan = build_plan(QuizInputs(quiz_name="   "))
        assert plan.title == "Document Quiz"


class TestBuildUserPromptText:
    def test_minimal_inputs_have_no_optional_sections(self):
        text = _build_user_prompt_text(QuizInputs(num_questions=5), context="DOC TEXT")
        assert "DOC TEXT" in text
        assert "5" in text
        assert "Focus topics:" not in text
        assert "Difficulty:" not in text
        assert "Question style:" not in text
        assert "Extra instructions:" not in text

    def test_all_optional_fields_render(self):
        inputs = QuizInputs(
            quiz_name="Cardio",
            num_questions=8,
            focus_topics="ECG",
            difficulty="hard",
            question_style="case scenarios",
            extra_instructions="No trivia.",
        )
        text = _build_user_prompt_text(inputs, context="DOC")
        assert "Focus topics: ECG" in text
        assert "Difficulty: hard" in text
        assert "Question style: case scenarios" in text
        assert "Extra instructions: No trivia." in text
        assert '"Cardio"' in text  # quiz title appears in the prompt

    def test_curly_brace_in_title_is_safe(self):
        # Regression guard: title must NOT be passed through a templating engine
        # that would try to interpret braces as variable names.
        text = _build_user_prompt_text(
            QuizInputs(quiz_name="{weird}", num_questions=1), context="DOC"
        )
        assert "{weird}" in text


class _FakeStructuredLLM:
    """Stub that captures the messages it was invoked with and returns a canned Quiz."""

    def __init__(self, canned: Quiz):
        self.canned = canned
        self.captured_messages = None

    def invoke(self, messages):
        self.captured_messages = messages
        return self.canned


class TestGenerateQuiz:
    def _docs(self) -> list[Document]:
        return [
            Document(page_content="Heart anatomy", metadata={"page": 1}),
            Document(page_content="Conduction system", metadata={"page": 2}),
        ]

    def _canned(self) -> Quiz:
        return Quiz(
            title="ignored — overridden by inputs.quiz_name when set",
            questions=[
                Question(
                    question="What pumps blood?",
                    options=[
                        Option(label="A", text="Heart"),
                        Option(label="B", text="Liver"),
                        Option(label="C", text="Lung"),
                        Option(label="D", text="Spleen"),
                    ],
                    correct_answer="A",
                    explanation="The heart is the muscular pump.",
                    source_page=1,
                )
            ],
        )

    def test_uses_quiz_inputs_signature(self, monkeypatch):
        fake = _FakeStructuredLLM(self._canned())
        monkeypatch.setattr(
            "app.quiz.generator.ChatOpenAI",
            lambda **_: type(
                "X", (), {"with_structured_output": lambda self, _: fake}
            )(),
        )

        inputs = QuizInputs(quiz_name="Cardio", num_questions=1, focus_topics="ECG")
        quiz = generate_quiz(self._docs(), inputs)

        assert isinstance(quiz, Quiz)
        assert quiz.title == "Cardio"  # overridden from inputs
        assert len(quiz.questions) == 1
        rendered = "\n".join(m.content for m in fake.captured_messages)
        assert "Focus topics: ECG" in rendered
        assert "Heart anatomy" in rendered  # context made it through

    def test_blank_title_falls_back(self, monkeypatch):
        fake = _FakeStructuredLLM(self._canned())
        monkeypatch.setattr(
            "app.quiz.generator.ChatOpenAI",
            lambda **_: type(
                "X", (), {"with_structured_output": lambda self, _: fake}
            )(),
        )
        quiz = generate_quiz(self._docs(), QuizInputs(num_questions=1))
        assert quiz.title == "Document Quiz"


@pytest.mark.asyncio
class TestPreviewPromptEndpoint:
    async def test_happy_path(self, client):
        body = {
            "quiz_name": "Cardio",
            "num_questions": 8,
            "model": "gpt-4o-mini",
            "focus_topics": "ECG",
            "difficulty": "medium",
            "question_style": "case scenarios",
            "extra_instructions": "",
        }
        resp = await client.post(
            "/api/preview-prompt", json=body, headers=_api_headers()
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["title"] == "Cardio"
        assert data["num_questions"] == 8
        assert data["focus_topics"] == "ECG"
        assert data["difficulty"] == "medium"
        assert data["document_source"]
        assert isinstance(data["rules"], list) and len(data["rules"]) >= 5

    async def test_defaults(self, client):
        resp = await client.post("/api/preview-prompt", json={}, headers=_api_headers())
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["title"] == "Document Quiz"
        assert data["num_questions"] == 10
        assert data["difficulty"] is None

    async def test_invalid_difficulty_returns_422(self, client):
        resp = await client.post(
            "/api/preview-prompt",
            json={"difficulty": "extreme"},
            headers=_api_headers(),
        )
        assert resp.status_code == 422

    async def test_invalid_model_returns_422(self, client):
        resp = await client.post(
            "/api/preview-prompt",
            json={"model": "gpt-5-imagined"},
            headers=_api_headers(),
        )
        assert resp.status_code == 422

    async def test_response_matches_build_plan(self, client):
        """Same-renderer guard: API response must equal build_plan() output."""
        body = {"quiz_name": "X", "num_questions": 3, "focus_topics": "alpha"}
        resp = await client.post(
            "/api/preview-prompt", json=body, headers=_api_headers()
        )
        assert resp.status_code == 200
        expected = build_plan(QuizInputs(**body)).model_dump()
        assert resp.json() == expected


def _fake_quiz() -> Quiz:
    return Quiz(
        title="placeholder",
        questions=[
            Question(
                question="What pumps blood?",
                options=[
                    Option(label="A", text="Heart"),
                    Option(label="B", text="Liver"),
                    Option(label="C", text="Lung"),
                    Option(label="D", text="Spleen"),
                ],
                correct_answer="A",
                explanation="The heart pumps blood.",
                source_page=1,
            )
        ],
    )


@pytest.mark.asyncio
class TestGenerateEndpointBackcompat:
    async def test_old_clients_still_work(self, client, monkeypatch):
        captured: dict = {}

        def fake_ingest(path):
            return [type("D", (), {"page_content": "x", "metadata": {"page": 1}})()]

        def fake_generate(documents, inputs):
            captured["inputs"] = inputs
            return _fake_quiz()

        monkeypatch.setattr("app.quiz.router.ingest_pdf", fake_ingest)
        monkeypatch.setattr("app.quiz.router.generate_quiz", fake_generate)

        files = {"pdf": ("x.pdf", b"%PDF-1.4 fake bytes", "application/pdf")}
        data = {"num_questions": "5", "model": "gpt-4o-mini", "quiz_name": "Old Client"}
        resp = await client.post(
            "/api/generate", files=files, data=data, headers=_api_headers()
        )

        assert resp.status_code == 200, resp.text
        assert resp.json()["title"] == "placeholder"
        assert captured["inputs"].quiz_name == "Old Client"
        assert captured["inputs"].num_questions == 5
        assert captured["inputs"].focus_topics == ""
        assert captured["inputs"].difficulty is None


@pytest.mark.asyncio
class TestGenerateEndpointNewFields:
    async def test_new_fields_wire_through(self, client, monkeypatch):
        captured: dict = {}

        monkeypatch.setattr(
            "app.quiz.router.ingest_pdf",
            lambda _: [type("D", (), {"page_content": "x", "metadata": {"page": 1}})()],
        )

        def fake_generate(documents, inputs):
            captured["inputs"] = inputs
            return _fake_quiz()

        monkeypatch.setattr("app.quiz.router.generate_quiz", fake_generate)

        files = {"pdf": ("x.pdf", b"%PDF-1.4 fake bytes", "application/pdf")}
        data = {
            "num_questions": "7",
            "focus_topics": "ECG",
            "difficulty": "hard",
            "question_style": "case scenarios",
            "extra_instructions": "No trivia.",
        }
        resp = await client.post(
            "/api/generate", files=files, data=data, headers=_api_headers()
        )

        assert resp.status_code == 200, resp.text
        assert captured["inputs"].focus_topics == "ECG"
        assert captured["inputs"].difficulty == "hard"
        assert captured["inputs"].question_style == "case scenarios"
        assert captured["inputs"].extra_instructions == "No trivia."

    async def test_invalid_difficulty_returns_422(self, client):
        files = {"pdf": ("x.pdf", b"%PDF-1.4 fake bytes", "application/pdf")}
        data = {"num_questions": "5", "difficulty": "extreme"}
        resp = await client.post(
            "/api/generate", files=files, data=data, headers=_api_headers()
        )
        assert resp.status_code == 422
        assert isinstance(resp.json()["detail"], list)

    async def test_invalid_model_returns_422(self, client):
        files = {"pdf": ("x.pdf", b"%PDF-1.4 fake bytes", "application/pdf")}
        data = {"num_questions": "5", "model": "gpt-5-imagined"}
        resp = await client.post(
            "/api/generate", files=files, data=data, headers=_api_headers()
        )
        assert resp.status_code == 422
        assert isinstance(resp.json()["detail"], list)

    async def test_non_pdf_returns_400(self, client):
        files = {"pdf": ("x.txt", b"not a pdf", "text/plain")}
        resp = await client.post(
            "/api/generate",
            files=files,
            data={"num_questions": "5"},
            headers=_api_headers(),
        )
        assert resp.status_code == 400
