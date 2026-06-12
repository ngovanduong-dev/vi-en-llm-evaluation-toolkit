"""Rubric scoring helpers for LLM evaluation records."""

from __future__ import annotations

from typing import Literal

from src.schemas import EvaluationRecord, RubricScores

Winner = Literal["A", "B", "Tie"]

SCORE_FIELDS = [
    "instruction_following",
    "correctness",
    "completeness",
    "clarity",
    "language_naturalness",
    "formatting",
    "safety",
]


def normalize_winner(value: str) -> Winner:
    normalized = value.strip().lower()

    if normalized in {"a", "response a", "model a"}:
        return "A"
    if normalized in {"b", "response b", "model b"}:
        return "B"
    if normalized in {"tie", "draw", "equal", "same"}:
        return "Tie"

    raise ValueError(f"Unsupported winner label: {value}")


def calculate_average_score(scores: RubricScores) -> float:
    values = [getattr(scores, field) for field in SCORE_FIELDS]
    return round(sum(values) / len(values), 2)


def score_band(score: float) -> str:
    if score >= 4.5:
        return "strong"
    if score >= 3.5:
        return "acceptable"
    if score >= 2.5:
        return "weak"
    return "poor"


def summarize_evaluation(record: EvaluationRecord) -> dict:
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