import io
import json
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

import pytest

from vi_en_eval.agreement import compare_technical_evaluations, main
from vi_en_eval.technical_dataset import load_technical_dataset

SCORE_FIELDS = (
    "instruction_following",
    "correctness",
    "edge_case_handling",
    "efficiency",
    "maintainability",
    "security_reliability",
    "explanation_quality",
)


def write_rows(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_inputs(tmp_path, winners_a, winners_b, source_count=None):
    count = max(len(winners_a), len(winners_b)) if source_count is None else source_count
    paths = tuple(tmp_path / name for name in ("prompts", "responses", "a", "b"))
    write_rows(
        paths[0],
        [
            {
                "id": "prompt",
                "language": "Bilingual",
                "task_type": "Coding",
                "prompt": "Nội dung nguồn / source prompt sentinel",
            }
        ],
    )
    write_rows(
        paths[1],
        [
            {
                "id": f"pair-{i}",
                "prompt_id": "prompt",
                "response_a": "raise RuntimeError('candidate-content-sentinel')",
                "response_b": "Phản hồi B / candidate-content-sentinel",
            }
            for i in range(count)
        ],
    )
    candidate = {
        "rubric_scores": dict.fromkeys(SCORE_FIELDS, 3),
        "rationale": "Lý do / candidate-rationale-sentinel",
        "detected_issues": [],
    }
    for path, winners, evaluator in ((paths[2], winners_a, "a"), (paths[3], winners_b, "b")):
        write_rows(
            path,
            [
                {
                    "id": f"{evaluator}-{i}",
                    "prompt_id": "prompt",
                    "response_pair_id": f"pair-{i}",
                    "candidate_a": candidate,
                    "candidate_b": candidate,
                    "winner": winner,
                    "confidence": 0.8,
                    "rationale": "Đánh giá / overall-rationale-sentinel",
                }
                for i, winner in enumerate(winners)
                if winner is not None
            ],
        )
    return paths


def cli_args(paths):
    return [
        value
        for flag, path in zip(
            ("--prompts", "--responses", "--evaluations-a", "--evaluations-b"), paths, strict=True
        )
        for value in (flag, str(path))
    ]


@pytest.mark.parametrize(
    ("a", "b", "matrix", "observed", "expected", "kappa"),
    [
        (["A", "B", "Tie"], ["A", "B", "Tie"], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1, 1 / 3, 1),
        # Six pairs: trace=4, row totals=(3,1,2), columns=(3,2,1).
        # Expected=(9+2+2)/36; kappa=(24-13)/(36-13)=11/23.
        (
            ["A", "A", "A", "B", "Tie", "Tie"],
            ["A", "A", "B", "B", "A", "Tie"],
            [[2, 1, 0], [0, 1, 0], [1, 0, 1]],
            2 / 3,
            13 / 36,
            11 / 23,
        ),
        (["A", "B"], ["B", "A"], [[0, 1, 0], [1, 0, 0], [0, 0, 0]], 0, 1 / 2, -1),
        (["Tie"], ["A"], [[0, 0, 0], [0, 0, 0], [1, 0, 0]], 0, 0, 0),
        (["Tie"], ["B"], [[0, 0, 0], [0, 0, 0], [0, 1, 0]], 0, 0, 0),
    ],
)
def test_hand_calculated_winner_statistics(tmp_path, a, b, matrix, observed, expected, kappa):
    result = compare_technical_evaluations(*write_inputs(tmp_path, a, b))
    assert result.is_valid
    stats = result.comparison["winner_agreement"]
    assert stats["labels"] == ["A", "B", "Tie"]
    assert (stats["rows"], stats["columns"]) == ("evaluator_a", "evaluator_b")
    assert stats["confusion_matrix"] == matrix
    assert stats["matched_pairs"] == len(a)
    assert stats["agreements"] == round(observed * len(a))
    assert stats["disagreements"] == len(a) - round(observed * len(a))
    assert stats["observed_agreement"] == pytest.approx(observed)
    assert stats["expected_agreement"] == pytest.approx(expected)
    assert stats["cohens_kappa"] == pytest.approx(kappa)
    assert stats["kappa_undefined_reason"] is None


@pytest.mark.parametrize("label", ["A", "B", "Tie"])
def test_identical_single_label_has_undefined_kappa(tmp_path, label):
    result = compare_technical_evaluations(*write_inputs(tmp_path, [label] * 3, [label] * 3))
    stats = result.comparison["winner_agreement"]
    assert stats["observed_agreement"] == 1
    assert stats["expected_agreement"] == 1
    assert stats["cohens_kappa"] is None
    assert stats["kappa_undefined_reason"] == "expected_agreement_is_one"
    assert all(record["winner_agrees"] for record in result.comparison["matched_evaluations"])


def test_missing_evaluations_are_explicit_and_not_in_agreement_denominator(tmp_path):
    paths = write_inputs(tmp_path, ["A", "B", None], [None, "B", "Tie"], source_count=4)
    comparison = compare_technical_evaluations(*paths).comparison
    assert comparison["coverage"] == {
        "source_response_pairs": 4,
        "evaluator_a_evaluated_pairs": 2,
        "evaluator_b_evaluated_pairs": 2,
        "evaluator_a_coverage": 0.5,
        "evaluator_b_coverage": 0.5,
        "matched_pairs": 1,
        "only_a_pair_ids": ["pair-0"],
        "only_b_pair_ids": ["pair-2"],
        "missing_a_pair_ids": ["pair-2", "pair-3"],
        "missing_b_pair_ids": ["pair-0", "pair-3"],
        "neither_pair_ids": ["pair-3"],
    }
    assert comparison["winner_agreement"]["observed_agreement"] == 1


@pytest.mark.parametrize(
    "a,b,count",
    [([], [], 0), ([], [], 2), (["A"], [], 2), ([], ["B"], 2), (["A", None], [None, "B"], 2)],
)
def test_empty_overlap_and_zero_denominators(tmp_path, a, b, count):
    paths = write_inputs(tmp_path, a, b, source_count=count)
    if count == 0:
        write_rows(paths[0], [])
    result = compare_technical_evaluations(*paths)
    assert result.is_valid
    comparison = result.comparison
    assert comparison["matched_evaluations"] == []
    stats = comparison["winner_agreement"]
    assert stats["confusion_matrix"] == [[0, 0, 0]] * 3
    assert stats["observed_agreement"] is None
    assert stats["expected_agreement"] is None
    assert stats["cohens_kappa"] is None
    assert stats["kappa_undefined_reason"] == "no_matched_pairs"
    assert comparison["rubric_score_agreement"]["exact_match_rate"] is None
    if count == 0:
        assert comparison["coverage"]["evaluator_a_coverage"] is None
        assert comparison["coverage"]["evaluator_b_coverage"] is None


def test_order_independence_and_repeatable_json(tmp_path, capsys):
    paths = write_inputs(tmp_path, ["A", "Tie", "B"], ["B", "Tie", "A"])
    prompts = read_rows(paths[0])
    prompts.append({**prompts[0], "id": "unused"})
    write_rows(paths[0], prompts)
    assert main([*cli_args(paths), "--json"]) == 0
    first = capsys.readouterr().out
    for path in paths:
        write_rows(path, list(reversed(read_rows(path))))
        assert main([*cli_args(paths), "--json"]) == 0
        assert capsys.readouterr().out == first
    for _ in range(2):
        assert main([*cli_args(paths), "--json"]) == 0
        assert capsys.readouterr().out == first
    records = json.loads(first)["comparison"]["matched_evaluations"]
    assert [r["response_pair_id"] for r in records] == ["pair-0", "pair-1", "pair-2"]
    assert records[0]["evaluation_id_a"] == "a-0"
    assert records[0]["evaluation_id_b"] == "b-0"


def test_scores_are_separate_and_rationales_are_opt_in(tmp_path, capsys):
    paths = write_inputs(tmp_path, ["A", "B"], ["A", "A"])
    rows = read_rows(paths[2])
    rows[0]["candidate_a"]["rubric_scores"]["correctness"] = 5
    rows[0]["candidate_b"]["rubric_scores"]["efficiency"] = 1
    write_rows(paths[2], rows)
    assert main([*cli_args(paths), "--json"]) == 0
    output = capsys.readouterr().out
    assert "sentinel" not in output
    comparison = json.loads(output)["comparison"]
    assert comparison["rubric_score_agreement"] == {
        "matched_pairs": 2,
        "exact_match_pairs": 1,
        "exact_match_rate": 0.5,
    }
    first, second = comparison["matched_evaluations"]
    assert first["winner_agrees"] and not first["scores_agree"]
    assert not second["winner_agrees"] and second["scores_agree"]
    assert first["human_adjudication_recommended"] and second["human_adjudication_recommended"]
    assert first["score_differences_a_minus_b"]["candidate_a"]["correctness"] == 2
    assert first["score_differences_a_minus_b"]["candidate_b"]["efficiency"] == -2
    assert main([*cli_args(paths), "--json", "--include-rationales"]) == 0
    output = capsys.readouterr().out
    decoded = json.dumps(json.loads(output), ensure_ascii=False)
    assert "Đánh giá" in decoded and "Lý do" in decoded
    assert "candidate-content-sentinel" not in output
    assert "source prompt sentinel" not in output
    assert (
        json.loads(output)["comparison"]["matched_evaluations"][0]["rationales"]["evaluator_a"][
            "overall"
        ]
        == rows[0]["rationale"]
    )


@pytest.mark.parametrize("file_index", [0, 1, 2, 3])
def test_duplicate_record_ids_in_any_collection_invalidate_all_metrics(tmp_path, file_index):
    paths = write_inputs(tmp_path, ["A"], ["A"])
    rows = read_rows(paths[file_index])
    write_rows(paths[file_index], rows + rows)
    result = compare_technical_evaluations(*paths)
    assert not result.is_valid and result.comparison is None
    loaded = result.evaluator_b if file_index == 3 else result.evaluator_a
    assert [issue.code for issue in loaded.issues] == ["duplicate_id"]
    assert not loaded.integrity_checked


@pytest.mark.parametrize("file_index,evaluator", [(2, "a"), (3, "b")])
@pytest.mark.parametrize("conflicting", [False, True])
def test_duplicate_pair_assessments_rejected_even_when_identical(
    tmp_path, file_index, evaluator, conflicting, capsys
):
    paths = write_inputs(tmp_path, ["A"], ["B"])
    rows = read_rows(paths[file_index])
    duplicate = {**deepcopy(rows[0]), "id": "another-id"}
    if conflicting:
        duplicate["winner"] = "Tie"
    write_rows(paths[file_index], [*rows, duplicate])
    # Preserve the pre-existing loader's broader contract.
    assert load_technical_dataset(paths[0], paths[1], paths[file_index]).is_valid
    result = compare_technical_evaluations(*paths)
    assert not result.is_valid and result.comparison is None
    assert result.issues[0].code == "duplicate_pair_assessment"
    assert result.issues[0].evaluator == evaluator
    assert result.issues[0].response_pair_id == "pair-0"
    assert result.issues[0].evaluation_ids == tuple(sorted([rows[0]["id"], "another-id"]))
    write_rows(paths[file_index], [duplicate, *rows])
    assert compare_technical_evaluations(*paths).to_dict() == result.to_dict()
    assert main(cli_args(paths)) == 1
    assert "duplicate_pair_assessment" in capsys.readouterr().out


@pytest.mark.parametrize(
    "file_index,field,value,code",
    [
        (1, "prompt_id", "missing", "missing_prompt"),
        (2, "prompt_id", "missing", "missing_prompt"),
        (3, "response_pair_id", "missing", "missing_response_pair"),
        (3, "prompt_id", "another-prompt", "prompt_reference_mismatch"),
    ],
)
def test_reference_failures_preserve_loader_diagnostics(tmp_path, file_index, field, value, code):
    paths = write_inputs(tmp_path, ["A"], ["A"])
    prompts = read_rows(paths[0])
    write_rows(paths[0], [*prompts, {**prompts[0], "id": "another-prompt"}])
    rows = read_rows(paths[file_index])
    rows[0][field] = value
    write_rows(paths[file_index], rows)
    result = compare_technical_evaluations(*paths)
    assert not result.is_valid and result.comparison is None
    loaded = result.evaluator_b if file_index == 3 else result.evaluator_a
    assert code in [issue.code for issue in loaded.issues]
    expected = load_technical_dataset(paths[0], paths[1], paths[3 if file_index == 3 else 2])
    assert loaded.to_dict() == expected.to_dict()


@pytest.mark.parametrize(
    "text,code",
    [
        ('{"private":', "malformed_json"),
        ('{"private":1,"private":2}', "duplicate_json_key"),
        ('{"private":NaN}', "non_finite_number"),
        ('{"private":Infinity}', "non_finite_number"),
        ("[]", "schema_validation_error"),
        ("", "blank_line"),
    ],
)
def test_transport_and_schema_errors_return_no_metrics(tmp_path, capsys, text, code):
    paths = write_inputs(tmp_path, ["A"], ["A"])
    paths[2].write_text(text + "\n", encoding="utf-8")
    assert main([*cli_args(paths), "--json"]) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["comparison"] is None and not payload["is_valid"]
    assert payload["validation"]["evaluator_a"]["issues"][0]["code"] == code
    assert "private" not in output
    assert main(cli_args(paths)) == 1
    output = capsys.readouterr().out
    assert "INVALID" in output and code in output and "no metrics computed" in output


def test_strict_score_schema_and_unknown_fields_remain_enforced(tmp_path):
    paths = write_inputs(tmp_path, ["A"], ["B"])
    rows = read_rows(paths[3])
    rows[0]["candidate_a"]["rubric_scores"]["correctness"] = True
    rows[0]["extra"] = "private-value-sentinel"
    write_rows(paths[3], rows)
    result = compare_technical_evaluations(*paths)
    assert not result.is_valid and result.comparison is None
    assert [i.field for i in result.evaluator_b.issues] == [
        "candidate_a.rubric_scores.correctness",
        "extra",
    ]
    assert "private-value-sentinel" not in json.dumps(result.to_dict())


@pytest.mark.parametrize(
    "failure,code",
    [("missing", "file_read_error"), ("directory", "file_read_error"), ("utf8", "invalid_utf8")],
)
def test_read_failures_are_sanitized(tmp_path, capsys, failure, code):
    paths = list(write_inputs(tmp_path, ["A"], ["B"]))
    if failure == "missing":
        paths[3] = tmp_path / "missing.jsonl"
    elif failure == "directory":
        paths[3] = tmp_path
    else:
        paths[3].write_bytes(b"private-value-sentinel\xff")
    assert main([*cli_args(paths), "--json"]) == 1
    output = capsys.readouterr().out
    assert "private-value-sentinel" not in output and "Traceback" not in output
    payload = json.loads(output)
    assert payload["comparison"] is None
    assert payload["validation"]["evaluator_b"]["issues"][0]["code"] == code


@pytest.mark.parametrize("change", ["prompt", "response"])
def test_changed_shared_source_between_loads_is_rejected(tmp_path, monkeypatch, change):
    paths = write_inputs(tmp_path, ["A"], ["B"])
    calls = 0

    def changing_loader(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            index, field = (0, "prompt") if change == "prompt" else (1, "response_a")
            rows = read_rows(paths[index])
            rows[0][field] = "changed source sentinel"
            write_rows(paths[index], rows)
        return load_technical_dataset(*args)

    monkeypatch.setattr("vi_en_eval.agreement.load_technical_dataset", changing_loader)
    result = compare_technical_evaluations(*paths)
    assert not result.is_valid and result.comparison is None
    assert result.issues[0].code == "source_changed"
    assert "changed source sentinel" not in json.dumps(result.to_dict())


def test_valid_human_output_and_usage_codes(tmp_path, capsys):
    paths = write_inputs(tmp_path, ["A"], ["B"])
    assert main(cli_args(paths)) == 0
    output = capsys.readouterr().out
    assert "VALID" in output and "matched=1" in output and "agreement is not accuracy" in output
    for args in ([], [*cli_args(paths), "--include-rationales"]):
        with pytest.raises(SystemExit) as error:
            main(args)
        assert error.value.code == 2


def test_installed_command_and_module_execute_comparison(tmp_path):
    paths = write_inputs(tmp_path, ["Tie"], ["Tie"])
    command = shutil.which("vi-en-compare")
    assert command is not None
    for prefix in ([command], [sys.executable, "-m", "vi_en_eval.agreement"]):
        completed = subprocess.run(
            [*prefix, *cli_args(paths), "--json"], capture_output=True, text=True, check=False
        )
        assert completed.returncode == 0 and completed.stderr == ""
        payload = json.loads(completed.stdout)
        assert payload["schema_version"] == 1
        assert payload["comparison"]["winner_agreement"]["cohens_kappa"] is None


@pytest.mark.parametrize("encoding", ["ascii", "cp1252"])
def test_unicode_json_survives_restricted_stdout_and_round_trips(tmp_path, encoding):
    paths = write_inputs(tmp_path, ["A"], ["B"])
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "vi_en_eval.agreement",
            *cli_args(paths),
            "--json",
            "--include-rationales",
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": encoding},
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert (
        report["comparison"]["matched_evaluations"][0]["rationales"]["evaluator_a"]["overall"]
        == "Đánh giá / overall-rationale-sentinel"
    )


@pytest.mark.parametrize(
    "encoding,displayed_name",
    [
        ("ascii", r"\u0111-\xe9-missing.jsonl"),
        ("cp1252", "\\u0111-é-missing.jsonl"),
        ("utf-8", "đ-é-missing.jsonl"),
    ],
)
@pytest.mark.parametrize("valid", [False, True])
def test_human_cli_handles_stdout_encoding(tmp_path, encoding, displayed_name, valid):
    folder = Path("data/agreement_example").resolve()
    paths = [
        folder / name
        for name in (
            "prompts.jsonl",
            "response_pairs.jsonl",
            "evaluations_a.jsonl",
            "evaluations_b.jsonl",
        )
    ]
    if not valid:
        paths[3] = tmp_path / "đ-é-missing.jsonl"
    completed = subprocess.run(
        [sys.executable, "-m", "vi_en_eval.agreement", *cli_args(paths)],
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": encoding},
    )
    assert completed.returncode == (0 if valid else 1)
    assert completed.stderr == b""
    output = completed.stdout.decode(encoding)
    if valid:
        assert output.startswith("VALID:") and "matched=6" in output
    else:
        assert output.startswith("INVALID:") and "file_read_error" in output
        assert displayed_name in output


def test_human_output_preserves_unicode_in_encodingless_capture(tmp_path):
    paths = list(write_inputs(tmp_path, ["A"], ["B"]))
    paths[3] = tmp_path / "đ-missing.jsonl"
    output = io.StringIO()
    with redirect_stdout(output):
        assert main(cli_args(paths)) == 1
    assert "đ-missing.jsonl" in output.getvalue()
    assert output.encoding is None


def test_evaluator_swap_transposes_matrix_without_changing_statistics(tmp_path):
    paths = write_inputs(
        tmp_path, ["A", "A", "A", "B", "Tie", "Tie"], ["A", "A", "B", "B", "A", "Tie"]
    )
    forward = compare_technical_evaluations(*paths).comparison["winner_agreement"]
    swapped = compare_technical_evaluations(paths[0], paths[1], paths[3], paths[2]).comparison[
        "winner_agreement"
    ]
    assert forward["confusion_matrix"] == [[2, 1, 0], [0, 1, 0], [1, 0, 1]]
    assert swapped["confusion_matrix"] == [[2, 0, 1], [1, 1, 0], [0, 0, 1]]
    for stats in (forward, swapped):
        assert stats["observed_agreement"] == pytest.approx(2 / 3)
        assert stats["cohens_kappa"] == pytest.approx(11 / 23)


def test_evaluation_ids_shared_across_files_do_not_override_pair_identity(tmp_path):
    paths = write_inputs(tmp_path, ["A", "B"], ["A", "B"])
    rows = read_rows(paths[3])
    # Same IDs in both files, deliberately assigned to different pairs.
    rows[0]["id"], rows[1]["id"] = "a-1", "a-0"
    write_rows(paths[3], list(reversed(rows)))
    comparison = compare_technical_evaluations(*paths).comparison
    assert comparison["winner_agreement"]["observed_agreement"] == 1
    assert comparison["winner_agreement"]["cohens_kappa"] == 1
    assert [
        (r["response_pair_id"], r["evaluation_id_a"], r["evaluation_id_b"])
        for r in comparison["matched_evaluations"]
    ] == [("pair-0", "a-0", "a-1"), ("pair-1", "a-1", "a-0")]


def test_bundled_example_matches_documented_arithmetic():
    folder = Path("data/agreement_example")
    result = compare_technical_evaluations(
        folder / "prompts.jsonl",
        folder / "response_pairs.jsonl",
        folder / "evaluations_a.jsonl",
        folder / "evaluations_b.jsonl",
    )
    assert result.is_valid
    comparison = result.comparison
    assert comparison["coverage"]["source_response_pairs"] == 9
    assert comparison["coverage"]["matched_pairs"] == 6
    assert comparison["coverage"]["only_a_pair_ids"] == ["pair-7"]
    assert comparison["coverage"]["only_b_pair_ids"] == ["pair-8"]
    assert comparison["coverage"]["neither_pair_ids"] == ["pair-9"]
    assert comparison["winner_agreement"]["confusion_matrix"] == [[2, 1, 0], [0, 1, 0], [1, 0, 1]]
    assert comparison["winner_agreement"]["cohens_kappa"] == pytest.approx(11 / 23)
