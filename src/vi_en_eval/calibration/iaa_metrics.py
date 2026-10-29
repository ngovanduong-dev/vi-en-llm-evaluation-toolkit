from __future__ import annotations

import math
from collections import Counter
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CohensKappaReport(BaseModel):
    """Pairwise inter-annotator agreement report using Cohen's Kappa."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sample_size: int = Field(ge=1)
    observed_agreement: float = Field(ge=0.0, le=1.0)
    expected_agreement: float = Field(ge=0.0, le=1.0)
    kappa: float | None = Field(ge=-1.0, le=1.0)
    undefined_reason: str | None = None
    interpretation_band: (
        Literal[
            "poor",
            "slight",
            "fair",
            "moderate",
            "substantial",
            "almost_perfect",
        ]
        | None
    )
    passes_production_threshold: bool


class FleissKappaReport(BaseModel):
    """Multi-rater inter-annotator agreement report using Fleiss' Kappa."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_items: int = Field(ge=1)
    num_raters_per_item: int = Field(ge=2)
    observed_agreement_bar: float = Field(ge=0.0, le=1.0)
    expected_agreement_bar: float = Field(ge=0.0, le=1.0)
    fleiss_kappa: float | None = Field(ge=-1.0, le=1.0)
    undefined_reason: str | None = None
    passes_production_threshold: bool


class SwapEvaluationPair(BaseModel):
    """Paired evaluation verdicts recorded before and after swapping candidate positions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str = Field(min_length=1, pattern=r"\S")
    forward_verdict: Literal["model_a", "model_b", "tie"]
    swapped_verdict: Literal["model_a", "model_b", "tie"]


class PositionSwapBiasReport(BaseModel):
    """Summary of position consistency and first-position preference bias across swapped evaluations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_pairs: int = Field(ge=1)
    consistent_count: int = Field(ge=0)
    inconsistent_item_ids: tuple[str, ...]
    consistency_rate: float = Field(ge=0.0, le=1.0)
    first_position_bias_rate: float = Field(ge=0.0, le=1.0)


def _interpret_landis_koch(
    kappa: float,
) -> Literal["poor", "slight", "fair", "moderate", "substantial", "almost_perfect"]:
    if kappa < 0.0:
        return "poor"
    if kappa < 0.20:
        return "slight"
    if kappa < 0.40:
        return "fair"
    if kappa < 0.60:
        return "moderate"
    if kappa < 0.80:
        return "substantial"
    return "almost_perfect"


def compute_cohens_kappa(
    rater_a_labels: tuple[str, ...] | list[str],
    rater_b_labels: tuple[str, ...] | list[str],
    production_threshold: float = 0.65,
) -> CohensKappaReport:
    """Compute Cohen's Kappa coefficient for two aligned sequences of categorical labels."""
    _validate_threshold(production_threshold)
    if len(rater_a_labels) != len(rater_b_labels):
        raise ValueError("Both label sequences must have identical length.")
    n = len(rater_a_labels)
    if n == 0:
        raise ValueError("Label sequences must not be empty.")

    matches = sum(a == b for a, b in zip(rater_a_labels, rater_b_labels, strict=True))
    counts_a, counts_b = Counter(rater_a_labels), Counter(rater_b_labels)
    expected_numerator = sum(count * counts_b[cat] for cat, count in counts_a.items())
    denominator = n * n - expected_numerator
    kappa = (n * matches - expected_numerator) / denominator if denominator else None
    return CohensKappaReport(
        sample_size=n,
        observed_agreement=matches / n,
        expected_agreement=expected_numerator / (n * n),
        kappa=kappa,
        undefined_reason="expected_agreement_is_one" if kappa is None else None,
        interpretation_band=_interpret_landis_koch(kappa) if kappa is not None else None,
        passes_production_threshold=kappa is not None and kappa >= production_threshold,
    )


def compute_fleiss_kappa(
    ratings_matrix: list[list[str]] | tuple[tuple[str, ...], ...],
    production_threshold: float = 0.60,
) -> FleissKappaReport:
    """Compute Fleiss' Kappa coefficient across N items rated by a fixed number of raters."""
    _validate_threshold(production_threshold)
    num_items = len(ratings_matrix)
    if num_items == 0:
        raise ValueError("ratings_matrix must contain at least one item.")

    num_raters = len(ratings_matrix[0])
    if num_raters < 2:
        raise ValueError("Each item must have at least 2 raters for Fleiss' Kappa.")

    for row in ratings_matrix:
        if len(row) != num_raters:
            raise ValueError(
                "All items in ratings_matrix must have the exact same number of raters."
            )

    total_decisions = num_items * num_raters
    category_totals: Counter[str] = Counter()
    agreement_numerator = 0
    for row in ratings_matrix:
        counts = Counter(row)
        category_totals.update(counts)
        agreement_numerator += sum(count * (count - 1) for count in counts.values())
    agreement_denominator = total_decisions * (num_raters - 1)
    expected_numerator = sum(count * count for count in category_totals.values())
    expected_denominator = total_decisions * total_decisions
    denominator = agreement_denominator * (expected_denominator - expected_numerator)
    kappa = (
        (agreement_numerator * expected_denominator - expected_numerator * agreement_denominator)
        / denominator
        if denominator
        else None
    )
    return FleissKappaReport(
        num_items=num_items,
        num_raters_per_item=num_raters,
        observed_agreement_bar=agreement_numerator / agreement_denominator,
        expected_agreement_bar=expected_numerator / expected_denominator,
        fleiss_kappa=kappa,
        undefined_reason="expected_agreement_is_one" if kappa is None else None,
        passes_production_threshold=kappa is not None and kappa >= production_threshold,
    )


def evaluate_position_swap_bias(
    pairs: list[SwapEvaluationPair] | tuple[SwapEvaluationPair, ...],
) -> PositionSwapBiasReport:
    """Evaluate verdict consistency when swapping Model A and Model B display positions."""
    if not pairs:
        raise ValueError("Swap evaluation pairs must not be empty.")

    if len({pair.item_id for pair in pairs}) != len(pairs):
        raise ValueError("Swap evaluation item IDs must be unique")
    inconsistent_ids: list[str] = []
    first_position_picks = 0

    for pair in pairs:
        if pair.forward_verdict == "model_a" and pair.swapped_verdict == "model_a":
            first_position_picks += 1

        is_consistent = (
            (pair.forward_verdict == "model_a" and pair.swapped_verdict == "model_b")
            or (pair.forward_verdict == "model_b" and pair.swapped_verdict == "model_a")
            or (pair.forward_verdict == "tie" and pair.swapped_verdict == "tie")
        )
        if not is_consistent:
            inconsistent_ids.append(pair.item_id)

    total = len(pairs)
    consistent_count = total - len(inconsistent_ids)
    return PositionSwapBiasReport(
        total_pairs=total,
        consistent_count=consistent_count,
        inconsistent_item_ids=tuple(inconsistent_ids),
        consistency_rate=consistent_count / total,
        first_position_bias_rate=first_position_picks / total,
    )


def _validate_threshold(threshold: float) -> None:
    if not math.isfinite(threshold) or not -1 <= threshold <= 1:
        raise ValueError("Threshold must be finite and between -1 and 1")
