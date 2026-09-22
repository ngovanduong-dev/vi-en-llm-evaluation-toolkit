import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from vi_en_eval.jsonl_validator import main, validate_jsonl


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def valid_evaluation_record() -> dict:
    return {
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
        "detected_issues": [
            {
                "category": "Localization",
                "severity": "Medium",
                "description": "Response B sounds fluent but misses the user's constraint.",
                "suggested_fix": "Preserve the requested tone and constraint in Vietnamese.",
            }
        ],
        "rationale": "Response A better preserves the user's intent and tone.",
    }


def test_valid_sample_evaluations_file_passes_validation():
    result = validate_jsonl("data/sample_evaluations.jsonl")

    assert result.is_valid
    assert result.valid_records == 3
    assert result.issues == []


def test_validator_rejects_malformed_json(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"id": "broken"\n', encoding="utf-8")

    result = validate_jsonl(path)

    assert not result.is_valid
    assert result.issues[0].code == "malformed_json"
    assert result.issues[0].line_number == 1


def test_validator_rejects_missing_required_field(tmp_path):
    row = valid_evaluation_record()
    del row["winner"]
    path = write_jsonl(tmp_path / "missing_field.jsonl", [row])

    result = validate_jsonl(path)

    assert not result.is_valid
    assert any(issue.field == "winner" for issue in result.issues)


def test_validator_rejects_invalid_winner_label(tmp_path):
    row = valid_evaluation_record()
    row["winner"] = "Response A"
    path = write_jsonl(tmp_path / "invalid_winner.jsonl", [row])

    result = validate_jsonl(path)

    assert not result.is_valid
    assert any(issue.field == "winner" for issue in result.issues)


def test_validator_rejects_score_outside_one_to_five(tmp_path):
    row = valid_evaluation_record()
    row["rubric_scores"]["correctness"] = 6
    path = write_jsonl(tmp_path / "bad_score.jsonl", [row])

    result = validate_jsonl(path)

    assert not result.is_valid
    assert any(issue.field == "rubric_scores.correctness" for issue in result.issues)


def test_validator_rejects_blank_rationale(tmp_path):
    row = valid_evaluation_record()
    row["rationale"] = "   "
    path = write_jsonl(tmp_path / "blank_rationale.jsonl", [row])

    result = validate_jsonl(path)

    assert not result.is_valid
    assert any(issue.field == "rationale" for issue in result.issues)


def test_validator_rejects_whitespace_only_record_id(tmp_path):
    row = valid_evaluation_record()
    row["id"] = "   "
    path = write_jsonl(tmp_path / "blank_id.jsonl", [row])

    result = validate_jsonl(path)

    assert not result.is_valid
    assert any(issue.field == "id" for issue in result.issues)


def test_validator_rejects_duplicate_ids(tmp_path):
    first = valid_evaluation_record()
    second = valid_evaluation_record()
    second["prompt_id"] = "prompt_test_002"
    second["response_pair_id"] = "pair_test_002"
    path = write_jsonl(tmp_path / "duplicate_ids.jsonl", [first, second])

    result = validate_jsonl(path)

    assert not result.is_valid
    assert result.valid_records == 1
    assert any(
        issue.code == "duplicate_id" and issue.field == "id" and issue.line_number == 2
        for issue in result.issues
    )


@pytest.mark.parametrize("schema_name", ["prompt", "response", "evaluation"])
def test_sample_jsonl_files_match_registered_schemas(schema_name):
    file_map = {
        "prompt": "data/sample_prompts.jsonl",
        "response": "data/sample_responses.jsonl",
        "evaluation": "data/sample_evaluations.jsonl",
    }

    result = validate_jsonl(file_map[schema_name], schema_name=schema_name)

    assert result.is_valid


def test_validator_rejects_unknown_schema():
    with pytest.raises(ValueError, match="Unknown schema 'unknown'"):
        validate_jsonl("data/sample_evaluations.jsonl", schema_name="unknown")


def test_cli_preserves_human_readable_output(capsys):
    exit_code = main(["data/sample_prompts.jsonl", "--schema", "prompt"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "VALID:" in captured.out
    assert "sample_prompts.jsonl" in captured.out
    assert "Valid records: 3/3" in captured.out


def test_cli_supports_machine_readable_output(capsys):
    exit_code = main(["data/sample_evaluations.jsonl", "--schema", "evaluation", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["is_valid"] is True
    assert payload["valid_records"] == 3


def test_cli_returns_nonzero_and_lists_issues(tmp_path, capsys):
    path = tmp_path / "invalid.jsonl"
    path.write_text("\n", encoding="utf-8")

    exit_code = main([str(path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "INVALID:" in captured.out
    assert "blank_line" in captured.out


@pytest.mark.parametrize(
    ("bad_line", "code"),
    [
        ('{"id":"a","id":"b"}', "duplicate_json_key"),
        ('{"outer":{"secret":1,"secret":2}}', "duplicate_json_key"),
        *[
            (f'{{"score":{literal}}}', "non_finite_number")
            for literal in ("NaN", "Infinity", "-Infinity")
        ],
        ("null", "schema_validation_error"),
        ("   {", "malformed_json"),
    ],
)
def test_file_transport_schema_and_id_rules_are_separate(tmp_path, bad_line, code):
    row = json.dumps(valid_evaluation_record())
    path = tmp_path / "mixed.jsonl"
    path.write_text("\n".join([bad_line, "", row, row]) + "\n", encoding="utf-8")
    result = validate_jsonl(path)
    assert result.total_lines == 4
    assert result.valid_records == 1
    assert [(issue.line_number, issue.code) for issue in result.issues] == [
        (1, code),
        (2, "blank_line"),
        (4, "duplicate_id"),
    ]
    if code == "malformed_json":
        assert "column 5" in result.issues[0].message
    if code in {"duplicate_json_key", "non_finite_number"}:
        assert "column" not in result.issues[0].message
        assert "secret" not in result.issues[0].message


@pytest.mark.parametrize("machine", [False, True])
@pytest.mark.parametrize("case", ["valid", "invalid", "missing", "invalid_utf8"])
def test_cli_subprocess_contract(tmp_path, machine, case):
    path = tmp_path / "input.jsonl"
    if case == "valid":
        write_jsonl(path, [valid_evaluation_record()])
    elif case == "invalid":
        path.write_text('{"private_marker":NaN}', encoding="utf-8")
    elif case == "invalid_utf8":
        path.write_bytes(b"private_marker\xff")
    command = [sys.executable, "-m", "vi_en_eval.jsonl_validator", str(path)]
    if machine:
        command.append("--json")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == (0 if case == "valid" else 1)
    assert result.stderr == ""
    assert "private_marker" not in result.stdout
    if machine:
        payload = json.loads(result.stdout)
        assert payload["file_path"] == str(path)
        assert payload["is_valid"] is (case == "valid")
        if case in {"missing", "invalid_utf8"}:
            assert payload["error"]["code"] == (
                "invalid_utf8" if case == "invalid_utf8" else "file_read_error"
            )
            assert "valid_records" not in payload
        else:
            assert set(payload) == {
                "file_path",
                "schema_name",
                "total_lines",
                "valid_records",
                "is_valid",
                "issues",
            }
    else:
        assert str(path) in result.stdout
        assert result.stdout.startswith(
            "VALID:" if case == "valid" else "INVALID:" if case == "invalid" else "ERROR:"
        )


@pytest.mark.parametrize("machine", [False, True])
@pytest.mark.parametrize("during_read", [False, True])
def test_cli_controls_oserror_without_exception_details(tmp_path, capsys, machine, during_read):
    args = [str(tmp_path / "input.jsonl")]
    if machine:
        args.append("--json")
    with patch.object(Path, "open") as mocked_open:
        if during_read:
            mocked_open.return_value.__enter__.return_value.__iter__.side_effect = OSError(
                "private_marker"
            )
        else:
            mocked_open.side_effect = PermissionError("private_marker")
        assert main(args) == 1
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "private_marker" not in captured.out
    assert "file_read_error" in captured.out
    if machine:
        assert json.loads(captured.out)["error"]["code"] == "file_read_error"


def test_cli_does_not_hide_programming_errors():
    with patch("vi_en_eval.jsonl_validator.validate_jsonl", side_effect=RuntimeError("defect")):
        with pytest.raises(RuntimeError, match="defect"):
            main(["input.jsonl"])


@pytest.mark.parametrize("score", [True, "1", 1.0])
def test_file_reports_coercible_scores_as_schema_errors(tmp_path, score):
    row = valid_evaluation_record()
    row["rubric_scores"]["correctness"] = score
    path = write_jsonl(tmp_path / "score.jsonl", [row])
    result = validate_jsonl(path)
    assert [(issue.code, issue.field) for issue in result.issues] == [
        ("schema_validation_error", "rubric_scores.correctness")
    ]
