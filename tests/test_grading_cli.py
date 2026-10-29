from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

from vi_en_eval.cli import main


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_ifeval_cli_and_failure(tmp_path, capsys):
    response = write(tmp_path, "response.txt", "Đà Nẵng")
    constraints = write(tmp_path, "constraints.json", '{"min_words":2,"required_keywords":["Đà"]}')
    assert main(["ifeval", "--response", response, "--constraints", constraints]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["schema_version"] == 1 and output["report"]["passed"]
    write(tmp_path, "response.txt", "")
    assert main(["ifeval", "--response", response, "--constraints", constraints]) == 1
    assert not json.loads(capsys.readouterr().out)["report"]["passed"]


@pytest.mark.parametrize(
    ("command", "option", "payload", "field"),
    [
        ("kappa", "ratings", {"rater_a_labels": ["A", "B"], "rater_b_labels": ["A", "B"]}, "kappa"),
        ("fleiss", "ratings", {"ratings_matrix": [["A", "A"], ["B", "B"]]}, "fleiss_kappa"),
        (
            "swap-bias",
            "pairs",
            {
                "pairs": [
                    {"item_id": "q", "forward_verdict": "model_a", "swapped_verdict": "model_b"}
                ]
            },
            "consistency_rate",
        ),
    ],
)
def test_calibration_commands(tmp_path, capsys, command, option, payload, field):
    path = write(tmp_path, "input.json", json.dumps(payload))
    assert main([command, f"--{option}", path]) == 0
    assert json.loads(capsys.readouterr().out)["report"][field] == 1


def test_full_ab_pipeline(tmp_path, capsys):
    a = write(tmp_path, "a.py", "def f() -> int: return 1")
    b = write(tmp_path, "b.py", "def f() -> int: return 0")
    fixture = write(tmp_path, "fixture.py", "assert f() == 1")
    spec = write(tmp_path, "constraints.json", '{"required_keywords":["def"]}')
    ratings = write(
        tmp_path, "ratings.json", '{"rater_a_labels":["A","B"],"rater_b_labels":["A","B"]}'
    )
    args = ["grade-ab", "--model-a", a, "--model-b", b, "--tests", fixture, "--function", "f"]
    assert main([*args, "--constraints", spec, "--ratings", ratings]) == 0
    report = json.loads(capsys.readouterr().out)["report"]
    assert report["code_comparison"]["winner"] == "model_a"
    assert report["cohens_kappa"]["kappa"] == 1
    assert report["instruction_following"]["model_a"]["passed"]
    write(tmp_path, "a.py", "def f() -> int: return 0")
    assert main(args) == 1
    assert (
        json.loads(capsys.readouterr().out)["report"]["code_comparison"]["winner"]
        == "tie_both_fail"
    )


@pytest.mark.parametrize(
    "payload",
    [
        "{",
        '{"unknown":1}',
        '{"rater_a_labels":[],"rater_b_labels":[]}',
        '{"a":1,"a":2}',
        '{"a":NaN}',
    ],
)
def test_cli_invalid_inputs(tmp_path, capsys, payload):
    path = write(tmp_path, "bad.json", payload)
    assert main(["kappa", "--ratings", path]) == 1
    output = capsys.readouterr()
    assert "error" in json.loads(output.out) and not output.err
    assert "Traceback" not in output.out


def test_cli_read_errors_and_usage(tmp_path, capsys):
    assert main(["kappa", "--ratings", str(tmp_path / "missing")]) == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "invalid_input"
    path = tmp_path / "invalid.json"
    path.write_bytes(b"\xff")
    assert main(["kappa", "--ratings", str(path)]) == 1
    capsys.readouterr()
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2


def test_invalid_optional_input_prevents_execution(tmp_path, capsys, monkeypatch):
    from vi_en_eval import cli

    def fail(*args, **kwargs):
        pytest.fail("Execution started before validation")

    monkeypatch.setattr(cli, "compare_code_candidates_ab", fail)
    source = write(tmp_path, "a.py", "pass")
    invalid = write(tmp_path, "ratings.json", "{}")
    assert (
        main(
            [
                "grade-ab",
                "--model-a",
                source,
                "--model-b",
                source,
                "--tests",
                source,
                "--ratings",
                invalid,
            ]
        )
        == 1
    )
    assert "error" in json.loads(capsys.readouterr().out)


def test_installed_cli_and_module(tmp_path):
    command = shutil.which("vi-en-grade")
    assert command is not None
    ratings = write(
        tmp_path, "ratings.json", '{"rater_a_labels":["A","B"],"rater_b_labels":["A","B"]}'
    )
    for prefix in ([command], [sys.executable, "-m", "vi_en_eval.cli"]):
        result = subprocess.run(
            [*prefix, "kappa", "--ratings", ratings],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
            env={k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}},
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["report"]["kappa"] == 1
