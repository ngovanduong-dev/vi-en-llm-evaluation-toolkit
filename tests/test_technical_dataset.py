import json
import shutil
import subprocess
from pathlib import Path

import pytest

from vi_en_eval.schemas import PromptRecord, ResponsePairRecord
from vi_en_eval.technical_dataset import load_technical_dataset, main
from vi_en_eval.technical_models import PairwiseTechnicalEvaluation

CASE_DATA = Path("data/technical_python")


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )
    return path


def sample_rows(file_name: str) -> list[dict]:
    return [json.loads(line) for line in (CASE_DATA / file_name).read_text().splitlines()]


def write_dataset(
    tmp_path: Path,
    prompts: list[dict] | None = None,
    response_pairs: list[dict] | None = None,
    evaluations: list[dict] | None = None,
) -> tuple[Path, Path, Path]:
    return (
        write_jsonl(
            tmp_path / "prompts.jsonl",
            sample_rows("prompts.jsonl") if prompts is None else prompts,
        ),
        write_jsonl(
            tmp_path / "response_pairs.jsonl",
            sample_rows("response_pairs.jsonl") if response_pairs is None else response_pairs,
        ),
        write_jsonl(
            tmp_path / "technical_evaluations.jsonl",
            sample_rows("technical_evaluations.jsonl") if evaluations is None else evaluations,
        ),
    )


def command_args(paths: tuple[Path, Path, Path]) -> list[str]:
    prompts, responses, evaluations = paths
    return [
        "--prompts",
        str(prompts),
        "--responses",
        str(responses),
        "--evaluations",
        str(evaluations),
    ]


def test_valid_linked_dataset_returns_typed_records():
    result = load_technical_dataset(
        CASE_DATA / "prompts.jsonl",
        CASE_DATA / "response_pairs.jsonl",
        CASE_DATA / "technical_evaluations.jsonl",
    )

    assert result.is_valid
    assert result.integrity_checked
    assert result.issues == ()
    assert result.dataset is not None
    assert (
        len(result.dataset.prompts),
        len(result.dataset.response_pairs),
        len(result.dataset.technical_evaluations),
    ) == (3, 3, 3)
    assert all(isinstance(record, PromptRecord) for record in result.dataset.prompts)
    assert all(isinstance(record, ResponsePairRecord) for record in result.dataset.response_pairs)
    assert all(
        isinstance(record, PairwiseTechnicalEvaluation)
        for record in result.dataset.technical_evaluations
    )


def test_malformed_evaluation_row_skips_integrity_checks(tmp_path):
    paths = write_dataset(tmp_path)
    paths[2].write_text('{"id": "broken"\n', encoding="utf-8")

    result = load_technical_dataset(*paths)

    assert not result.is_valid
    assert not result.integrity_checked
    assert result.dataset is None
    assert [(issue.record_type, issue.code) for issue in result.issues] == [
        ("technical_evaluation", "malformed_json")
    ]


@pytest.mark.parametrize("bad_row", ['{"id":"first","id":"second"}', '{"score":NaN}'])
def test_strict_json_policy_reaches_technical_loader(tmp_path, bad_row):
    paths = write_dataset(tmp_path)
    paths[2].write_text(bad_row + "\n", encoding="utf-8")

    result = load_technical_dataset(*paths)

    assert not result.integrity_checked
    assert [issue.code for issue in result.issues] == [
        "duplicate_json_key" if "second" in bad_row else "non_finite_number"
    ]
    assert bad_row not in result.issues[0].message


def test_wrong_technical_model_shape_is_a_schema_failure(tmp_path):
    paths = write_dataset(tmp_path)
    paths[2].write_text("[]\n", encoding="utf-8")

    result = load_technical_dataset(*paths)

    assert not result.integrity_checked
    assert [(issue.code, issue.line_number) for issue in result.issues] == [
        ("schema_validation_error", 1)
    ]


def test_duplicate_ids_are_rejected_without_choosing_a_record(tmp_path):
    prompts = sample_rows("prompts.jsonl")
    prompts.insert(1, dict(prompts[0]))
    paths = write_dataset(tmp_path, prompts=prompts)

    result = load_technical_dataset(*paths)

    assert not result.integrity_checked
    assert result.dataset is None
    assert [(issue.code, issue.record_type, issue.line_number) for issue in result.issues] == [
        ("duplicate_id", "prompt", 2)
    ]


def test_missing_prompt_is_reported_after_file_validation(tmp_path):
    prompts = sample_rows("prompts.jsonl")[1:]
    paths = write_dataset(tmp_path, prompts=prompts)

    result = load_technical_dataset(*paths)

    assert result.integrity_checked
    assert result.dataset is None
    assert [(issue.code, issue.record_type) for issue in result.issues] == [
        ("missing_prompt", "response_pair"),
        ("missing_prompt", "technical_evaluation"),
    ]


def test_missing_response_pair_is_reported(tmp_path):
    evaluations = sample_rows("technical_evaluations.jsonl")
    evaluations[0]["response_pair_id"] = "missing_pair"
    paths = write_dataset(tmp_path, evaluations=evaluations)

    result = load_technical_dataset(*paths)

    assert result.integrity_checked
    assert [(issue.code, issue.referenced_id) for issue in result.issues] == [
        ("missing_response_pair", "missing_pair")
    ]


def test_prompt_reference_mismatch_is_reported(tmp_path):
    evaluations = sample_rows("technical_evaluations.jsonl")
    evaluations[0]["prompt_id"] = evaluations[1]["prompt_id"]
    paths = write_dataset(tmp_path, evaluations=evaluations)

    result = load_technical_dataset(*paths)

    assert result.integrity_checked
    assert [(issue.code, issue.record_id) for issue in result.issues] == [
        ("prompt_reference_mismatch", evaluations[0]["id"])
    ]


def test_issue_order_and_json_output_are_deterministic(tmp_path):
    pairs = sample_rows("response_pairs.jsonl")[:1]
    evaluations = sample_rows("technical_evaluations.jsonl")[:1]
    pairs[0]["prompt_id"] = "missing_prompt_for_pair"
    evaluations[0]["prompt_id"] = "missing_prompt_for_evaluation"
    evaluations[0]["response_pair_id"] = "missing_pair"
    paths = write_dataset(tmp_path, prompts=[], response_pairs=pairs, evaluations=evaluations)

    first = load_technical_dataset(*paths)
    second = load_technical_dataset(*paths)

    assert first.to_dict() == second.to_dict()
    assert [issue.code for issue in first.issues] == [
        "missing_prompt",
        "missing_prompt",
        "missing_response_pair",
    ]
    assert [issue.record_type for issue in first.issues] == [
        "response_pair",
        "technical_evaluation",
        "technical_evaluation",
    ]


def test_cli_successful_human_output(capsys):
    paths = (
        CASE_DATA / "prompts.jsonl",
        CASE_DATA / "response_pairs.jsonl",
        CASE_DATA / "technical_evaluations.jsonl",
    )

    assert main(command_args(paths)) == 0
    output = capsys.readouterr().out
    assert output.startswith("VALID: technical dataset")
    assert "technical_evaluation: 3/3 records" in output
    assert "Integrity: checked" in output


def test_cli_successful_json_output(capsys):
    paths = (
        CASE_DATA / "prompts.jsonl",
        CASE_DATA / "response_pairs.jsonl",
        CASE_DATA / "technical_evaluations.jsonl",
    )

    assert main([*command_args(paths), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["is_valid"] is True
    assert payload["integrity_checked"] is True
    assert [file_result["valid_records"] for file_result in payload["files"]] == [3, 3, 3]
    assert payload["issues"] == []


def test_cli_invalid_dataset_returns_one_and_lists_issue(tmp_path, capsys):
    paths = write_dataset(tmp_path)
    paths[2].write_text("not json\n", encoding="utf-8")

    assert main(command_args(paths)) == 1
    output = capsys.readouterr().out
    assert output.startswith("INVALID: technical dataset")
    assert "malformed_json" in output
    assert "Integrity: not checked" in output
    assert "not json" not in output


def test_missing_file_is_a_sanitized_read_failure(tmp_path, capsys):
    paths = write_dataset(tmp_path)
    missing_path = tmp_path / "private_missing_name.jsonl"

    assert main(command_args((missing_path, paths[1], paths[2]))) == 1
    output = capsys.readouterr().out
    assert "file_read_error" in output
    assert "Unable to read input file" in output
    assert "WinError" not in output


def test_invalid_utf8_is_distinct_from_read_failure(tmp_path, capsys):
    paths = write_dataset(tmp_path)
    paths[2].write_bytes(b"private_content\xff")

    assert main([*command_args(paths), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert [issue["code"] for issue in payload["issues"]] == ["invalid_utf8"]
    assert "private_content" not in json.dumps(payload)


def test_installed_dataset_command_supports_help():
    command = shutil.which("vi-en-dataset")
    assert command is not None

    completed = subprocess.run(
        [command, "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "--prompts" in completed.stdout
    assert "--responses" in completed.stdout
    assert "--evaluations" in completed.stdout
    assert completed.stderr == ""
