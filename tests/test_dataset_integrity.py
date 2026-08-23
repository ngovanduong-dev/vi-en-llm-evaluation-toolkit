from vi_en_eval.dataset_integrity import (
    DatasetIntegrityIssue,
    validate_technical_dataset_integrity,
)
from vi_en_eval.schemas import PromptRecord, ResponsePairRecord
from vi_en_eval.technical_models import PairwiseTechnicalEvaluation


def make_prompt(record_id: str = "prompt_001") -> PromptRecord:
    return PromptRecord.model_validate(
        {
            "id": record_id,
            "language": "English",
            "task_type": "Coding",
            "prompt": "Compare the two technical responses.",
        }
    )


def make_response_pair(
    record_id: str = "pair_001",
    prompt_id: str = "prompt_001",
) -> ResponsePairRecord:
    return ResponsePairRecord.model_validate(
        {
            "id": record_id,
            "prompt_id": prompt_id,
            "response_a": "Candidate A response.",
            "response_b": "Candidate B response.",
        }
    )


def make_technical_evaluation(
    record_id: str = "technical_eval_001",
    prompt_id: str = "prompt_001",
    response_pair_id: str = "pair_001",
) -> PairwiseTechnicalEvaluation:
    scores = {
        "instruction_following": 4,
        "correctness": 4,
        "edge_case_handling": 4,
        "efficiency": 4,
        "maintainability": 4,
        "security_reliability": 4,
        "explanation_quality": 4,
    }
    candidate = {
        "rubric_scores": scores,
        "detected_issues": [],
        "rationale": "The response satisfies the technical requirements.",
    }
    return PairwiseTechnicalEvaluation.model_validate(
        {
            "id": record_id,
            "prompt_id": prompt_id,
            "response_pair_id": response_pair_id,
            "candidate_a": candidate,
            "candidate_b": candidate,
            "winner": "Tie",
            "confidence": 0.8,
            "rationale": "The responses are technically equivalent.",
        }
    )


def test_valid_linked_dataset_has_no_integrity_issues():
    issues = validate_technical_dataset_integrity(
        [make_prompt()],
        [make_response_pair()],
        [make_technical_evaluation()],
    )

    assert issues == []


def test_response_pair_reports_missing_prompt():
    issues = validate_technical_dataset_integrity(
        [],
        [make_response_pair(prompt_id="prompt_missing")],
        [],
    )

    assert issues == [
        DatasetIntegrityIssue(
            code="missing_prompt",
            record_type="response_pair",
            record_id="pair_001",
            field="prompt_id",
            referenced_id="prompt_missing",
            message="Response pair 'pair_001' references missing prompt 'prompt_missing'",
        )
    ]


def test_technical_evaluation_reports_missing_prompt():
    issues = validate_technical_dataset_integrity(
        [make_prompt()],
        [make_response_pair()],
        [make_technical_evaluation(prompt_id="prompt_missing")],
    )

    missing_prompt_issue = next(issue for issue in issues if issue.code == "missing_prompt")
    assert missing_prompt_issue == DatasetIntegrityIssue(
        code="missing_prompt",
        record_type="technical_evaluation",
        record_id="technical_eval_001",
        field="prompt_id",
        referenced_id="prompt_missing",
        message="Technical evaluation 'technical_eval_001' references missing prompt 'prompt_missing'",
    )


def test_technical_evaluation_reports_missing_response_pair():
    issues = validate_technical_dataset_integrity(
        [make_prompt()],
        [],
        [make_technical_evaluation(response_pair_id="pair_missing")],
    )

    assert issues == [
        DatasetIntegrityIssue(
            code="missing_response_pair",
            record_type="technical_evaluation",
            record_id="technical_eval_001",
            field="response_pair_id",
            referenced_id="pair_missing",
            message=(
                "Technical evaluation 'technical_eval_001' references missing response pair "
                "'pair_missing'"
            ),
        )
    ]


def test_technical_evaluation_reports_prompt_reference_mismatch():
    issues = validate_technical_dataset_integrity(
        [make_prompt("prompt_001"), make_prompt("prompt_002")],
        [make_response_pair(prompt_id="prompt_002")],
        [make_technical_evaluation(prompt_id="prompt_001")],
    )

    assert issues == [
        DatasetIntegrityIssue(
            code="prompt_reference_mismatch",
            record_type="technical_evaluation",
            record_id="technical_eval_001",
            field="response_pair_id",
            referenced_id="pair_001",
            message=(
                "Technical evaluation 'technical_eval_001' references prompt 'prompt_001', "
                "but response pair 'pair_001' references prompt 'prompt_002'"
            ),
        )
    ]


def test_duplicate_prompt_ids_are_reported():
    issues = validate_technical_dataset_integrity(
        [make_prompt(), make_prompt()],
        [],
        [],
    )

    assert issues == [
        DatasetIntegrityIssue(
            code="duplicate_id",
            record_type="prompt",
            record_id="prompt_001",
            field="id",
            referenced_id=None,
            message="Duplicate prompt id 'prompt_001'",
        )
    ]


def test_duplicate_response_pair_ids_are_reported():
    response_pairs = [make_response_pair(), make_response_pair(prompt_id="prompt_002")]
    issues = validate_technical_dataset_integrity(
        [make_prompt(), make_prompt("prompt_002")],
        response_pairs,
        [make_technical_evaluation(prompt_id="prompt_002")],
    )
    reversed_issues = validate_technical_dataset_integrity(
        [make_prompt(), make_prompt("prompt_002")],
        list(reversed(response_pairs)),
        [make_technical_evaluation(prompt_id="prompt_002")],
    )

    expected = [
        DatasetIntegrityIssue(
            code="duplicate_id",
            record_type="response_pair",
            record_id="pair_001",
            field="id",
            referenced_id=None,
            message="Duplicate response pair id 'pair_001'",
        )
    ]
    assert issues == expected
    assert reversed_issues == expected


def test_duplicate_technical_evaluation_ids_are_reported():
    issues = validate_technical_dataset_integrity(
        [make_prompt()],
        [make_response_pair()],
        [make_technical_evaluation(), make_technical_evaluation()],
    )

    assert issues == [
        DatasetIntegrityIssue(
            code="duplicate_id",
            record_type="technical_evaluation",
            record_id="technical_eval_001",
            field="id",
            referenced_id=None,
            message="Duplicate technical evaluation id 'technical_eval_001'",
        )
    ]


def test_multiple_integrity_issues_are_returned_together():
    issues = validate_technical_dataset_integrity(
        [make_prompt(), make_prompt()],
        [make_response_pair(prompt_id="prompt_missing")],
        [make_technical_evaluation(response_pair_id="pair_missing")],
    )

    assert len(issues) == 3
    assert {
        (
            issue.code,
            issue.record_type,
            issue.record_id,
            issue.field,
            issue.referenced_id,
        )
        for issue in issues
    } == {
        ("duplicate_id", "prompt", "prompt_001", "id", None),
        ("missing_prompt", "response_pair", "pair_001", "prompt_id", "prompt_missing"),
        (
            "missing_response_pair",
            "technical_evaluation",
            "technical_eval_001",
            "response_pair_id",
            "pair_missing",
        ),
    }
