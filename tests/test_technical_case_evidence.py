from pathlib import Path

import pytest

from tests.fixtures.technical_case_implementations import (
    call_isolation_candidate_a,
    iterable_mean_candidate_a,
    iterable_mean_candidate_b,
    make_call_isolation_candidate_b,
    stable_dedup_candidate_a,
    stable_dedup_candidate_b,
)
from vi_en_eval._json import decode_json
from vi_en_eval.dataset_integrity import validate_technical_dataset_integrity
from vi_en_eval.schemas import PromptRecord, ResponsePairRecord
from vi_en_eval.technical_models import PairwiseTechnicalEvaluation

CASE_DATA = Path("data/technical_python")


def load_records(path: Path, model_type: type):
    return [model_type.model_validate(decode_json(line)) for line in path.read_text().splitlines()]


def load_case_evaluations() -> dict[str, PairwiseTechnicalEvaluation]:
    evaluations = load_records(
        CASE_DATA / "technical_evaluations.jsonl",
        PairwiseTechnicalEvaluation,
    )
    return {evaluation.id: evaluation for evaluation in evaluations}


def test_each_case_record_is_structurally_valid():
    prompts = load_records(CASE_DATA / "prompts.jsonl", PromptRecord)
    response_pairs = load_records(CASE_DATA / "response_pairs.jsonl", ResponsePairRecord)
    evaluations = load_records(
        CASE_DATA / "technical_evaluations.jsonl",
        PairwiseTechnicalEvaluation,
    )

    assert len(prompts) == len(response_pairs) == len(evaluations) == 3
    assert all(type(evaluation.confidence) is float for evaluation in evaluations)


def test_case_pack_relationships_are_internally_consistent():
    prompts = load_records(CASE_DATA / "prompts.jsonl", PromptRecord)
    response_pairs = load_records(CASE_DATA / "response_pairs.jsonl", ResponsePairRecord)
    evaluations = load_records(
        CASE_DATA / "technical_evaluations.jsonl",
        PairwiseTechnicalEvaluation,
    )

    assert validate_technical_dataset_integrity(prompts, response_pairs, evaluations) == []


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], 0.0),
        ([-2.0, 0.0], 0.0),
        ([-2.0, 2.0, 4.0], 3.0),
    ],
)
def test_iterable_mean_candidates_meet_literal_sequence_oracles(values, expected):
    assert iterable_mean_candidate_a(values) == expected
    assert iterable_mean_candidate_b(values) == expected


def test_one_shot_iterable_is_the_discriminating_mean_oracle():
    values = [2.0, -1.0, 4.0]
    expected = 3.0

    assert iterable_mean_candidate_a(iter(values)) == 0.0
    assert iterable_mean_candidate_b(iter(values)) == expected


def test_repeated_call_is_the_discriminating_state_leak_oracle():
    candidate_b = make_call_isolation_candidate_b()

    assert call_isolation_candidate_a(["ant"]) == {"a": ["ant"]}
    assert call_isolation_candidate_a(["bear"]) == {"b": ["bear"]}
    assert candidate_b(["ant"]) == {"a": ["ant"]}
    assert candidate_b(["bear"]) == {"a": ["ant"], "b": ["bear"]}


def test_unhashable_input_is_the_discriminating_dedup_oracle():
    items = [["x"], ["y"], ["x"]]
    expected = [["x"], ["y"]]

    with pytest.raises(TypeError, match="unhashable"):
        stable_dedup_candidate_a(items)
    assert stable_dedup_candidate_b(items) == expected


def test_stored_judgments_match_the_observed_discriminating_evidence():
    evaluations = load_case_evaluations()
    mean = evaluations["tech_eval_python_iterable_mean_001"]
    state = evaluations["tech_eval_python_call_isolation_002"]
    dedup = evaluations["tech_eval_python_stable_dedup_003"]

    assert mean.winner == "B"
    assert "one-shot generator" in mean.candidate_a.detected_issues[0].description
    assert "returns 0.0" in mean.rationale

    assert state.winner == "A"
    assert "persists across invocations" in state.candidate_b.detected_issues[0].description
    assert "second result" in state.rationale

    assert dedup.winner == "B"
    assert "raises TypeError" in dedup.candidate_a.detected_issues[0].description
    assert "unhashable input domain" in dedup.rationale
