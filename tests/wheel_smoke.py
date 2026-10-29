"""Run with a clean wheel environment's Python -I, outside the source checkout."""

import json
import math
import os
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

from vi_en_eval import agreement


def main() -> None:
    example = Path(sys.argv[1]).resolve()
    assert not Path.cwd().resolve().is_relative_to(example.parents[1]), "Run outside checkout"
    module = Path(agreement.__file__).resolve()
    assert module.is_relative_to(Path(sys.prefix).resolve()), module
    command = Path(sysconfig.get_path("scripts")) / (
        "vi-en-compare.exe" if os.name == "nt" else "vi-en-compare"
    )
    completed = subprocess.run(
        [
            str(command),
            "--prompts",
            str(example / "prompts.jsonl"),
            "--responses",
            str(example / "response_pairs.jsonl"),
            "--evaluations-a",
            str(example / "evaluations_a.jsonl"),
            "--evaluations-b",
            str(example / "evaluations_b.jsonl"),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if key not in {"PYTHONPATH", "PYTHONHOME"}
        },
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == "", completed.stderr
    report = json.loads(completed.stdout)
    assert report["schema_version"] == 1 and report["is_valid"] is True
    comparison = report["comparison"]
    coverage = comparison["coverage"]
    assert coverage == {
        "source_response_pairs": 9,
        "evaluator_a_evaluated_pairs": 7,
        "evaluator_b_evaluated_pairs": 7,
        "evaluator_a_coverage": 7 / 9,
        "evaluator_b_coverage": 7 / 9,
        "matched_pairs": 6,
        "only_a_pair_ids": ["pair-7"],
        "only_b_pair_ids": ["pair-8"],
        "missing_a_pair_ids": ["pair-8", "pair-9"],
        "missing_b_pair_ids": ["pair-7", "pair-9"],
        "neither_pair_ids": ["pair-9"],
    }
    stats = comparison["winner_agreement"]
    assert stats["matched_pairs"] == 6
    assert stats["confusion_matrix"] == [[2, 1, 0], [0, 1, 0], [1, 0, 1]]
    assert math.isclose(stats["cohens_kappa"], 11 / 23, rel_tol=1e-12)
    smoke_grading_command()
    print(f"Installed module: {module}")
    print("Wheel comparison passed: 6 matched, coverage 7/9 each, expected matrix and kappa=11/23")


def smoke_grading_command() -> None:
    command = Path(sysconfig.get_path("scripts")) / (
        "vi-en-grade.exe" if os.name == "nt" else "vi-en-grade"
    )
    with tempfile.TemporaryDirectory(prefix="grading_smoke_") as directory:
        root = Path(directory)
        for name, source in (
            ("a.py", "def solve() -> int: return 1"),
            ("b.py", "def solve() -> int: return 0"),
            ("fixtures.py", "assert solve() == 1"),
            ("constraints.json", '{"required_keywords":["solve"]}'),
            ("ratings.json", '{"rater_a_labels":["A","B"],"rater_b_labels":["A","B"]}'),
        ):
            (root / name).write_text(source, encoding="utf-8")
        completed = subprocess.run(
            [
                str(command),
                "grade-ab",
                "--model-a",
                "a.py",
                "--model-b",
                "b.py",
                "--tests",
                "fixtures.py",
                "--function",
                "solve",
                "--constraints",
                "constraints.json",
                "--ratings",
                "ratings.json",
            ],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr or completed.stdout
        report = json.loads(completed.stdout)["report"]
        assert report["code_comparison"]["winner"] == "model_a"
        assert report["instruction_following"]["model_a"]["passed"]
        assert report["cohens_kappa"]["kappa"] == 1.0
        print("Wheel grading passed: fixtures, constraints, and agreement")


if __name__ == "__main__":
    main()
