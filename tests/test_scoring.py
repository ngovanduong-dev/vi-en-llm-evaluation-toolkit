import pytest

from vi_en_eval.schemas import EvaluationRecord
from vi_en_eval.scoring import (
    calculate_average_score,
    normalize_winner,
    score_band,
    summarize_evaluation,
)


def sample_record() -> EvaluationRecord:
    return EvaluationRecord.model_validate(
        {
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
            "rationale": "Response A better preserves tone and intent.",
        }
    )


def test_normalize_winner_accepts_common_labels():
    assert normalize_winner("response a") == "A"
    assert normalize_winner("Model B") == "B"
    assert normalize_winner("draw") == "Tie"


def test_normalize_winner_rejects_unknown_label():
    with pytest.raises(ValueError):
        normalize_winner("winner is first response")


def test_calculate_average_score():
    record = sample_record()

    assert calculate_average_score(record.rubric_scores) == 4.57


def test_score_band():
    assert score_band(4.8) == "strong"
    assert score_band(3.8) == "acceptable"
    assert score_band(2.8) == "weak"
    assert score_band(1.8) == "poor"


def test_summarize_evaluation():
    summary = summarize_evaluation(sample_record())

    assert summary["id"] == "eval_test_001"
    assert summary["winner"] == "A"
    assert summary["average_score"] == 4.57
    assert summary["score_band"] == "strong"
