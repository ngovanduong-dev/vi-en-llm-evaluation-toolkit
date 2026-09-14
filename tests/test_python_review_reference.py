"""Reviewed fixtures for the portfolio's average-positive counterexamples."""

import ast
import inspect
from pathlib import Path

import pytest


def average_positive(numbers):
    positives = []
    for value in numbers:
        if value > 0:
            positives.append(value)
    return sum(positives) / len(numbers)


def test_reviewed_fixture_is_only_a_colon_repair():
    sample = (
        Path(__file__).resolve().parents[1]
        / "portfolio_samples/technical_response_review/01_python_code_review.md"
    ).read_text(encoding="utf-8")
    original = sample.split("```python\n", 1)[1].split("```", 1)[0]
    with pytest.raises(SyntaxError) as error:
        ast.parse(original)
    assert error.value.lineno == 4
    repaired = original.replace("if value > 0\n", "if value > 0:\n", 1)
    assert ast.dump(ast.parse(repaired)) == ast.dump(ast.parse(inspect.getsource(average_positive)))


def test_colon_repair_still_raises_on_empty_input():
    with pytest.raises(ZeroDivisionError):
        average_positive([])


@pytest.mark.parametrize(
    ("numbers", "observed"),
    [([-2, 0, -5], 0.0), ([10, -5, 0, 20], 7.5), ([1, 2, 3], 2.0)],
)
def test_colon_repair_counterexamples(numbers, observed):
    assert average_positive(numbers) == observed
