"""Tests for quiz inputs, plan, and prompt rendering."""

import pytest
from pydantic import ValidationError

from app.quiz.generator import (
    SYSTEM_PROMPT,
    SYSTEM_RULES,
    build_plan,
    DOCUMENT_PLACEHOLDER,
    _build_user_prompt_text,
)
from app.quiz.models import QuizInputs, QuizPlan


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
