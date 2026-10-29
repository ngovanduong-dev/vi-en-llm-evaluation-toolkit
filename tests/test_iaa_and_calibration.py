from __future__ import annotations

from fractions import Fraction
from itertools import product

import pytest
from pydantic import ValidationError

from vi_en_eval.calibration import (
    SwapEvaluationPair,
    compute_cohens_kappa,
    compute_fleiss_kappa,
    evaluate_position_swap_bias,
)


def test_cohen_known_contingency_table_and_exact_threshold():
    # Rows [2,1,0], [0,1,0], [1,0,1]: Po=4/6, Pe=13/36, kappa=11/23.
    a = ["A", "A", "A", "B", "Tie", "Tie"]
    b = ["A", "A", "B", "B", "A", "Tie"]
    report = compute_cohens_kappa(a, b, production_threshold=11 / 23)
    assert report.observed_agreement == pytest.approx(2 / 3)
    assert report.expected_agreement == pytest.approx(13 / 36)
    assert report.kappa == pytest.approx(11 / 23)
    assert report.passes_production_threshold
    assert not compute_cohens_kappa(
        a, b, production_threshold=11 / 23 + 1e-8
    ).passes_production_threshold
    assert compute_cohens_kappa(b, a).kappa == report.kappa
    assert compute_cohens_kappa(a * 3, b * 3).kappa == report.kappa


def test_fleiss_known_fraction_and_invariance():
    ratings = [["A", "A", "A"], ["B", "B", "B"], ["T", "T", "T"], ["A", "A", "B"]]
    report = compute_fleiss_kappa(ratings)
    assert report.observed_agreement_bar == pytest.approx(5 / 6)
    assert report.expected_agreement_bar == pytest.approx(25 / 72)
    assert report.fleiss_kappa == pytest.approx(35 / 47)
    assert report.passes_production_threshold
    assert (
        compute_fleiss_kappa([row[::-1] for row in ratings[::-1]]).fleiss_kappa
        == report.fleiss_kappa
    )
    assert not compute_fleiss_kappa(
        ratings, production_threshold=35 / 47 + 1e-8
    ).passes_production_threshold


def test_degenerate_marginals_are_undefined_not_perfect():
    cohen = compute_cohens_kappa(["A"] * 3, ["A"] * 3)
    fleiss = compute_fleiss_kappa([["A", "A"], ["A", "A"]])
    assert cohen.kappa is None and cohen.interpretation_band is None
    assert fleiss.fleiss_kappa is None
    for report in (cohen, fleiss):
        assert report.undefined_reason == "expected_agreement_is_one"
        assert not report.passes_production_threshold
        assert "null" in report.model_dump_json()
    assert compute_cohens_kappa(["A"], ["B"]).kappa == 0


def test_negative_and_perfect_agreement():
    assert compute_cohens_kappa(["A", "B"], ["B", "A"]).kappa == -1
    assert compute_cohens_kappa(["A", "B"], ["A", "B"]).kappa == 1
    assert compute_fleiss_kappa([["A", "B"], ["B", "A"]]).fleiss_kappa == -1
    assert compute_fleiss_kappa([["A", "A"], ["B", "B"]]).fleiss_kappa == 1


@pytest.mark.parametrize(("a", "b"), [([], []), (["a"], [])])
def test_invalid_cohen_sequences(a, b):
    with pytest.raises(ValueError):
        compute_cohens_kappa(a, b)


@pytest.mark.parametrize("matrix", [[], [[]], [["a"]], [["a", "b"], ["a"]]])
def test_invalid_fleiss_matrix(matrix):
    with pytest.raises(ValueError):
        compute_fleiss_kappa(matrix)


@pytest.mark.parametrize("threshold", [-1.1, 1.1, float("nan"), float("inf")])
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError):
        compute_cohens_kappa(["a"], ["b"], threshold)
    with pytest.raises(ValueError):
        compute_fleiss_kappa([["a", "b"]], threshold)


@pytest.mark.parametrize(
    ("value", "band"),
    [
        (-0.1, "poor"),
        (0, "slight"),
        (0.2, "fair"),
        (0.4, "moderate"),
        (0.6, "substantial"),
        (0.8, "almost_perfect"),
    ],
)
def test_interpretation_intervals(value, band):
    from vi_en_eval.calibration.iaa_metrics import _interpret_landis_koch

    assert _interpret_landis_koch(value) == band


def test_exhaustive_small_cohen_tables_against_fraction_formula():
    sequences = list(product(("A", "B"), repeat=3))
    for a, b in product(sequences, repeat=2):
        observed = Fraction(sum(x == y for x, y in zip(a, b, strict=True)), 3)
        expected = sum(Fraction(a.count(c) * b.count(c), 9) for c in ("A", "B"))
        kappa = float((observed - expected) / (1 - expected)) if expected != 1 else None
        actual = compute_cohens_kappa(a, b).kappa
        assert actual == pytest.approx(kappa) if kappa is not None else actual is None


def test_every_swap_verdict_pair():
    labels = ("model_a", "model_b", "tie")
    pairs = [
        SwapEvaluationPair(item_id=str(i), forward_verdict=a, swapped_verdict=b)
        for i, (a, b) in enumerate(product(labels, repeat=2))
    ]
    report = evaluate_position_swap_bias(pairs)
    assert report.total_pairs == 9 and report.consistent_count == 3
    assert report.inconsistent_item_ids == ("0", "2", "4", "5", "6", "7")
    assert report.consistency_rate == 1 / 3
    assert report.first_position_bias_rate == 1 / 9


def test_swap_input_validation():
    with pytest.raises(ValueError, match="empty"):
        evaluate_position_swap_bias([])
    pair = SwapEvaluationPair(item_id="q", forward_verdict="tie", swapped_verdict="tie")
    with pytest.raises(ValueError, match="unique"):
        evaluate_position_swap_bias([pair, pair])
    with pytest.raises(ValidationError):
        SwapEvaluationPair(item_id=" ", forward_verdict="model_a", swapped_verdict="tie")
