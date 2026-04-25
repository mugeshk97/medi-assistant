"""Tests for quiz inputs, plan, and prompt rendering."""

import pytest
from pydantic import ValidationError

from app.quiz.models import QuizInputs


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
