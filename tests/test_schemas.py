import pytest
from pydantic import ValidationError

from vi_en_eval.schemas import DetectedIssue, EvaluationRecord, PromptRecord, ResponsePairRecord


def valid_evaluation_record() -> dict:
    return {
        "id": "eval_test_001",
        "prompt_id": "prompt_test_001",
        "response_pair_id": "pair_test_001",
        "language": "Bilingual",
        "task_type": "Translation",
        "winner": "A",
        "rubric_scores": {
            "instruction_following": 5,
            "correctness": 4,
            "completeness": 4,
            "clarity": 5,
            "language_naturalness": 5,
            "formatting": 4,
            "safety": 5,
        },
        "detected_issues": [],
        "rationale": "Response A better preserves the user's intent and tone.",
    }


@pytest.mark.parametrize("field", ["id", "prompt"])
def test_prompt_record_rejects_whitespace_only_text_fields(field):
    payload = {
        "id": "prompt_test_001",
        "language": "Vietnamese",
        "task_type": "General",
        "prompt": "Summarize the article in Vietnamese.",
    }
    payload[field] = "   "

    with pytest.raises(ValidationError) as exc_info:
        PromptRecord.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (field,)


def test_prompt_record_rejects_whitespace_only_constraint_items():
    payload = {
        "id": "prompt_test_001",
        "language": "Vietnamese",
        "task_type": "General",
        "prompt": "Summarize the article in Vietnamese.",
        "expected_constraints": ["Use a professional tone.", "   "],
    }

    with pytest.raises(ValidationError) as exc_info:
        PromptRecord.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == ("expected_constraints", 1)


@pytest.mark.parametrize(
    "field",
    ["id", "prompt_id", "response_a", "response_b", "model_a", "model_b"],
)
def test_response_pair_rejects_whitespace_only_text_fields(field):
    payload = {
        "id": "pair_test_001",
        "prompt_id": "prompt_test_001",
        "response_a": "Response A",
        "response_b": "Response B",
        "model_a": "synthetic_model_a",
        "model_b": "synthetic_model_b",
    }
    payload[field] = "   "

    with pytest.raises(ValidationError) as exc_info:
        ResponsePairRecord.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("field", ["id", "prompt_id", "response_pair_id", "rationale"])
def test_evaluation_record_rejects_whitespace_only_text_fields(field):
    payload = valid_evaluation_record()
    payload[field] = "   "

    with pytest.raises(ValidationError) as exc_info:
        EvaluationRecord.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("field", ["category", "description", "suggested_fix"])
def test_detected_issue_rejects_whitespace_only_text_fields(field):
    payload = {
        "category": "Localization",
        "severity": "Medium",
        "description": "The response uses unnatural Vietnamese phrasing.",
        "suggested_fix": "Use terminology natural to the target locale.",
    }
    payload[field] = "   "

    with pytest.raises(ValidationError) as exc_info:
        DetectedIssue.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (field,)
