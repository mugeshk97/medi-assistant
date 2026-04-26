"""Tests for quiz inputs, plan, and prompt rendering."""

import pytest
from pydantic import ValidationError

from langchain_core.documents import Document

from app.quiz.generator import (
    EXCERPT_MAX_CHARS,
    SYSTEM_PROMPT,
    SYSTEM_RULES,
    _build_user_prompt_text,
    build_document_preview,
    build_plan,
    generate_quiz,
    _build_context,
)
from app.quiz.models import (
    DocumentPreview,
    Option,
    Question,
    Quiz,
    QuizInputs,
    QuizPlan,
    GenerateRequest,
)

def _api_headers() -> dict:
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

    def test_all_fields_set(self):
        inputs = QuizInputs(
            quiz_name="Cardio Basics", num_questions=12, model="gpt-4o",
            focus_topics="ECG, arrhythmias", difficulty="medium",
            question_style="case scenarios", extra_instructions="Avoid trivia.",
        )
        assert inputs.difficulty == "medium"

    def test_strips_whitespace(self):
        inputs = QuizInputs(quiz_name="  Cardio  ", focus_topics="  topic  ")
        assert inputs.quiz_name == "Cardio"

    @pytest.mark.parametrize("n", [0, 51, -1])
    def test_num_questions_out_of_range(self, n):
        with pytest.raises(ValidationError):
            QuizInputs(num_questions=n)

    def test_model_not_in_allowlist(self):
        with pytest.raises(ValidationError):
            QuizInputs(model="gpt-5-imagined")

    @pytest.mark.parametrize("d", ["", "EASY", "extreme", "Medium"])
    def test_difficulty_invalid(self, d):
        if d == "":
            assert QuizInputs(difficulty=d).difficulty is None
        else:
            with pytest.raises(ValidationError):
                QuizInputs(difficulty=d)

class TestQuizPlan:
    def test_construct_full_plan(self):
        plan = QuizPlan(
            document=DocumentPreview(filename="x.pdf", pages=2, excerpt="hello"),
            prompt="prompt"
        )
        assert plan.document.filename == "x.pdf"
        assert plan.prompt == "prompt"

class TestDocumentPreview:
    def test_construct(self):
        dp = DocumentPreview(filename="cardio.pdf", pages=3, excerpt="hello")
        assert dp.filename == "cardio.pdf"

    def test_round_trip(self):
        dp = DocumentPreview(filename="cardio.pdf", pages=3, excerpt="hello")
        assert DocumentPreview.model_validate(dp.model_dump()) == dp

class TestSystemRules:
    def test_rules_non_empty(self):
        assert len(SYSTEM_RULES) >= 5

class TestBuildPlan:
    def _doc(self) -> DocumentPreview:
        return DocumentPreview(filename="cardio.pdf", pages=3, excerpt="hello")

    def test_full_inputs_round_trip(self):
        inputs = QuizInputs(quiz_name="Cardio Basics", num_questions=12, model="gpt-4o")
        plan = build_plan(inputs, self._doc(), "context")
        assert "context" in plan.prompt
        assert "Cardio Basics" in plan.prompt
        assert plan.document == self._doc()

class TestBuildDocumentPreview:
    def test_page_dedup(self):
        docs = [Document(page_content="a", metadata={"page": 1}), Document(page_content="b", metadata={"page": 1}), Document(page_content="c", metadata={"page": 2})]
        assert build_document_preview(docs, "x.pdf").pages == 2

    def test_excerpt_truncation(self):
        docs = [Document(page_content="y"*1000, metadata={"page": 1})]
        assert len(build_document_preview(docs, "x.pdf").excerpt) == EXCERPT_MAX_CHARS

    def test_missing_page_metadata_excluded(self):
        docs = [Document(page_content="a", metadata={"page": 1}), Document(page_content="b", metadata={})]
        assert build_document_preview(docs, "x.pdf").pages == 1

class TestBuildUserPromptText:
    def test_minimal_inputs_have_no_optional_sections(self):
        text = _build_user_prompt_text(QuizInputs(num_questions=5), "DOC TEXT")
        assert "5" in text
        assert "DOC TEXT" in text
        assert "Focus topics:" not in text

    def test_all_optional_fields_render(self):
        inputs = QuizInputs(quiz_name="Cardio", num_questions=8, focus_topics="ECG")
        text = _build_user_prompt_text(inputs, "DOC")
        assert "Focus topics: ECG" in text
        assert '"Cardio"' in text
        assert "DOC" in text

    def test_curly_brace_in_title_is_safe(self):
        text = _build_user_prompt_text(QuizInputs(quiz_name="{weird}", num_questions=1), "DOC")
        assert "{weird}" in text

class _FakeStructuredLLM:
    def __init__(self, canned: Quiz):
        self.canned = canned
        self.captured_messages = None
    def invoke(self, messages):
        self.captured_messages = messages
        return self.canned

def _fake_quiz() -> Quiz:
    return Quiz(
        title="Generated Title",
        questions=[Question(question="Q?", options=[Option(label="A", text="O1"), Option(label="B", text="O2"), Option(label="C", text="O3"), Option(label="D", text="O4")], correct_answer="A", explanation="E", source_page=1)]
    )

class TestGenerateQuiz:
    def test_uses_strings(self, monkeypatch):
        fake = _FakeStructuredLLM(_fake_quiz())
        monkeypatch.setattr("app.quiz.generator.ChatOpenAI", lambda **_: type("X", (), {"with_structured_output": lambda self, _: fake})())
        quiz = generate_quiz("my prompt", "gpt-4o-mini")
        assert quiz.title == "Generated Title"
        rendered = "\n".join(m.content for m in fake.captured_messages)
        assert "my prompt" in rendered

@pytest.mark.asyncio
class TestPreviewPromptEndpoint:
    def _stub_ingest(self, monkeypatch, docs):
        monkeypatch.setattr("app.quiz.router.ingest_pdf", lambda _: docs)

    async def test_happy_path(self, client, monkeypatch):
        self._stub_ingest(monkeypatch, [Document(page_content="Heart pumps blood.", metadata={"page": 1})])
        files = {"pdf": ("cardio.pdf", b"%PDF-1.4 fake bytes", "application/pdf")}
        data = {"quiz_name": "Cardio", "num_questions": "8", "model": "gpt-4o-mini", "focus_topics": "ECG", "difficulty": "medium", "question_style": "case scenarios", "extra_instructions": ""}
        resp = await client.post("/api/preview-prompt", files=files, data=data, headers=_api_headers())
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "prompt" in body
        assert "Heart pumps blood." in body["prompt"]
        assert "document" in body
        assert body["document"]["filename"] == "cardio.pdf"
        assert "title" not in body

    async def test_response_matches_build_plan(self, client, monkeypatch):
        canned_docs = [Document(page_content="alpha beta", metadata={"page": 1})]
        self._stub_ingest(monkeypatch, canned_docs)
        files = {"pdf": ("foo.pdf", b"%PDF-1.4 fake bytes", "application/pdf")}
        data = {"quiz_name": "X", "num_questions": "3", "focus_topics": "alpha"}
        resp = await client.post("/api/preview-prompt", files=files, data=data, headers=_api_headers())
        assert resp.status_code == 200
        expected_inputs = QuizInputs(quiz_name="X", num_questions=3, focus_topics="alpha")
        expected_doc = build_document_preview(canned_docs, "foo.pdf")
        expected = build_plan(expected_inputs, expected_doc, _build_context(canned_docs)).model_dump()
        assert resp.json() == expected

@pytest.mark.asyncio
class TestGenerateEndpoint:
    async def test_generate_from_request(self, client, monkeypatch):
        captured = {}
        def fake_generate(prompt, model):
            captured["prompt"] = prompt
            captured["model"] = model
            return _fake_quiz()
        monkeypatch.setattr("app.quiz.router.generate_quiz", fake_generate)
        
        req = GenerateRequest(prompt="Make a quiz", model="gpt-4o-mini")
        resp = await client.post("/api/generate", json=req.model_dump(), headers=_api_headers())
        
        assert resp.status_code == 200
        assert resp.json()["title"] == "Generated Title"
        assert captured["prompt"] == "Make a quiz"

    async def test_invalid_model_returns_422(self, client):
        req = {"prompt": "p", "model": "gpt-5-imagined"}
        resp = await client.post("/api/generate", json=req, headers=_api_headers())
        assert resp.status_code == 422
