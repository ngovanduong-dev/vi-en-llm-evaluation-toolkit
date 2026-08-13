import json
from pathlib import Path

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
