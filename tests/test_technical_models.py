from copy import deepcopy

import pytest
from pydantic import BaseModel, ValidationError

from vi_en_eval.technical_models import (
    CandidateTechnicalAssessment,
    PairwiseTechnicalEvaluation,
    TechnicalIssue,
    TechnicalRubricScores,
)

TECHNICAL_RUBRIC_FIELDS = (
    "instruction_following",
    "correctness",
    "edge_case_handling",
    "efficiency",
    "maintainability",
    "security_reliability",
    "explanation_quality",
)


def valid_scores(score: int = 4) -> dict:
    return {
        "instruction_following": score,
        "correctness": score,
        "edge_case_handling": score,
        "efficiency": score,
        "maintainability": score,
        "security_reliability": score,
        "explanation_quality": score,
    }


def valid_issue() -> dict:
    return {
        "category": "API/Contract",
        "severity": "High",
        "description": "The response calls an API that does not exist.",
        "suggested_fix": "Use the documented client method.",
    }


def valid_candidate(score: int = 4) -> dict:
    return {
        "rubric_scores": valid_scores(score),
        "detected_issues": [valid_issue()],
        "rationale": "The response is technically sound apart from the documented issue.",
    }


def valid_pairwise_evaluation() -> dict:
    return {
        "id": "technical_eval_001",
        "prompt_id": "prompt_001",
        "response_pair_id": "pair_001",
        "candidate_a": valid_candidate(5),
        "candidate_b": {
            "rubric_scores": valid_scores(3),
            "detected_issues": [],
            "rationale": "The response works but is less complete and maintainable.",
        },
        "winner": "A",
        "confidence": 0.9,
        "rationale": "Candidate A provides the stronger technical solution overall.",
    }


def test_valid_complete_pairwise_technical_evaluation():
    evaluation = PairwiseTechnicalEvaluation.model_validate(valid_pairwise_evaluation())

    assert evaluation.id == "technical_eval_001"
    assert evaluation.candidate_a.rubric_scores.correctness == 5
    assert evaluation.candidate_b.rubric_scores.correctness == 3
    assert evaluation.candidate_a.detected_issues[0].category.value == "API/Contract"
    assert evaluation.candidate_b.detected_issues == []
    assert evaluation.winner == "A"
    assert evaluation.confidence == 0.9


def test_pairwise_technical_evaluation_json_round_trip():
    original = PairwiseTechnicalEvaluation.model_validate(valid_pairwise_evaluation())

    serialized = original.model_dump_json()
    reconstructed = PairwiseTechnicalEvaluation.model_validate_json(serialized)

    assert reconstructed == original


@pytest.mark.parametrize("field", TECHNICAL_RUBRIC_FIELDS)
@pytest.mark.parametrize("score", [1, 5])
def test_technical_rubric_dimensions_accept_boundary_scores(field, score):
    payload = valid_scores()
    payload[field] = score

    scores = TechnicalRubricScores.model_validate(payload)

    assert getattr(scores, field) == score


@pytest.mark.parametrize("field", TECHNICAL_RUBRIC_FIELDS)
@pytest.mark.parametrize(
    ("score", "error_type"),
    [(0, "greater_than_equal"), (6, "less_than_equal")],
)
def test_technical_rubric_dimensions_reject_out_of_range_scores(field, score, error_type):
    payload = valid_scores()
    payload[field] = score

    with pytest.raises(ValidationError) as exc_info:
        TechnicalRubricScores.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (field,)
    assert exc_info.value.errors()[0]["type"] == error_type


@pytest.mark.parametrize("confidence", [0, 1, 0.0, 1.0, 0.5, 0.9])
def test_evaluator_confidence_accepts_numeric_values(confidence):
    payload = valid_pairwise_evaluation()
    payload["confidence"] = confidence

    evaluation = PairwiseTechnicalEvaluation.model_validate(payload)

    assert evaluation.confidence == confidence


@pytest.mark.parametrize("confidence", ["0.9", True, False])
def test_evaluator_confidence_rejects_non_numeric_input(confidence):
    payload = valid_pairwise_evaluation()
    payload["confidence"] = confidence

    with pytest.raises(ValidationError):
        PairwiseTechnicalEvaluation.model_validate(payload)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_evaluator_confidence_rejects_values_outside_zero_to_one(confidence):
    payload = valid_pairwise_evaluation()
    payload["confidence"] = confidence

    with pytest.raises(ValidationError):
        PairwiseTechnicalEvaluation.model_validate(payload)


def test_pairwise_evaluation_rejects_unsupported_winner():
    payload = valid_pairwise_evaluation()
    payload["winner"] = "Both"

    with pytest.raises(ValidationError):
        PairwiseTechnicalEvaluation.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [("category", "Framework Bug"), ("severity", "Critical")],
)
def test_technical_issue_rejects_invalid_category_or_severity(field, value):
    payload = valid_issue()
    payload[field] = value

    with pytest.raises(ValidationError):
        TechnicalIssue.model_validate(payload)


@pytest.mark.parametrize("field", ["id", "prompt_id", "response_pair_id", "rationale"])
def test_pairwise_evaluation_rejects_blank_required_text(field):
    payload = valid_pairwise_evaluation()
    payload[field] = "   "

    with pytest.raises(ValidationError) as exc_info:
        PairwiseTechnicalEvaluation.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (field,)


def test_candidate_assessment_rejects_blank_rationale():
    payload = valid_candidate()
    payload["rationale"] = "   "

    with pytest.raises(ValidationError):
        CandidateTechnicalAssessment.model_validate(payload)


def test_technical_issue_rejects_blank_description():
    payload = valid_issue()
    payload["description"] = "   "

    with pytest.raises(ValidationError):
        TechnicalIssue.model_validate(payload)


@pytest.mark.parametrize(
    ("model_type", "payload"),
    [
        (TechnicalIssue, valid_issue()),
        (TechnicalRubricScores, valid_scores()),
        (CandidateTechnicalAssessment, valid_candidate()),
        (PairwiseTechnicalEvaluation, valid_pairwise_evaluation()),
    ],
)
def test_technical_models_forbid_extra_fields(model_type: type[BaseModel], payload: dict):
    payload_with_extra = deepcopy(payload)
    payload_with_extra["unexpected"] = "value"

    with pytest.raises(ValidationError) as exc_info:
        model_type.model_validate(payload_with_extra)

    assert exc_info.value.errors()[0]["type"] == "extra_forbidden"


@pytest.mark.parametrize(
    "container_path",
    [
        pytest.param(("candidate_a",), id="candidate-assessment"),
        pytest.param(("candidate_a", "rubric_scores"), id="rubric-scores"),
        pytest.param(("candidate_a", "detected_issues", 0), id="technical-issue"),
    ],
)
def test_pairwise_evaluation_rejects_nested_extra_fields(container_path):
    payload = valid_pairwise_evaluation()
    nested_container = payload
    for path_part in container_path:
        nested_container = nested_container[path_part]
    nested_container["unexpected"] = "value"

    with pytest.raises(ValidationError) as exc_info:
        PairwiseTechnicalEvaluation.model_validate(payload)

    assert exc_info.value.errors()[0]["loc"] == (*container_path, "unexpected")
    assert exc_info.value.errors()[0]["type"] == "extra_forbidden"
