"""Rubric scoring helpers for LLM evaluation records."""

from __future__ import annotations

from typing import Final, Literal, TypeAlias

from vi_en_eval.schemas import EvaluationRecord, RubricScores

Winner: TypeAlias = Literal["A", "B", "Tie"]
EvaluationSummary: TypeAlias = dict[str, str | float | int]

SCORE_FIELDS: Final[tuple[str, ...]] = (
    "instruction_following",
    "correctness",
    "completeness",
    "clarity",
    "language_naturalness",
    "formatting",
    "safety",
)


def normalize_winner(value: str) -> Winner:
    """Normalize a supported human-readable winner label."""

    normalized = value.strip().lower()

    if normalized in {"a", "response a", "model a"}:
        return "A"
    if normalized in {"b", "response b", "model b"}:
        return "B"
    if normalized in {"tie", "draw", "equal", "same"}:
        return "Tie"

    raise ValueError(f"Unsupported winner label: {value}")


def calculate_average_score(scores: RubricScores) -> float:
    """Calculate the mean score across all rubric dimensions."""

    return scores.average()


def score_band(score: float) -> str:
    """Map an average score to its existing qualitative band."""

    if score >= 4.5:
        return "strong"
    if score >= 3.5:
        return "acceptable"
    if score >= 2.5:
        return "weak"
    return "poor"


def summarize_evaluation(record: EvaluationRecord) -> EvaluationSummary:
    """Create the compact evaluation summary used by report exports."""

    average_score = calculate_average_score(record.rubric_scores)

    return {
        "id": record.id,
        "prompt_id": record.prompt_id,
        "response_pair_id": record.response_pair_id,
        "language": record.language.value,
        "task_type": record.task_type.value,
        "winner": record.winner,
        "average_score": average_score,
        "score_band": score_band(average_score),
        "issue_count": len(record.detected_issues),
        "rationale": record.rationale,
    }
