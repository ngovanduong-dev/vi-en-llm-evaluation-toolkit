"""JSON command-line reports for deterministic verification and calibration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from vi_en_eval._json import decode_json
from vi_en_eval.calibration import (
    SwapEvaluationPair,
    compute_cohens_kappa,
    compute_fleiss_kappa,
    evaluate_position_swap_bias,
)
from vi_en_eval.verifiers import (
    ASTAnalysisPolicy,
    IFEvalConstraintSpec,
    compare_code_candidates_ab,
    verify_instruction_following,
)


class _Ratings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rater_a_labels: list[str]
    rater_b_labels: list[str]
    production_threshold: float = Field(default=0.65, ge=-1, le=1, allow_inf_nan=False)


class _MultiRatings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ratings_matrix: list[list[str]]
    production_threshold: float = Field(default=0.60, ge=-1, le=1, allow_inf_nan=False)


class _Swaps(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pairs: list[SwapEvaluationPair]


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _cohen(path: str) -> dict[str, Any]:
    ratings = _Ratings.model_validate(decode_json(_read(path)))
    return compute_cohens_kappa(
        ratings.rater_a_labels,
        ratings.rater_b_labels,
        ratings.production_threshold,
    ).model_dump(mode="json")


def _run(args: argparse.Namespace) -> tuple[dict[str, Any], bool]:
    if args.command == "ifeval":
        response_spec = IFEvalConstraintSpec.model_validate(decode_json(_read(args.constraints)))
        verified = verify_instruction_following(_read(args.response), response_spec)
        return verified.model_dump(mode="json"), verified.passed
    if args.command == "kappa":
        return _cohen(args.ratings), True
    if args.command == "fleiss":
        ratings = _MultiRatings.model_validate(decode_json(_read(args.ratings)))
        return compute_fleiss_kappa(
            ratings.ratings_matrix, ratings.production_threshold
        ).model_dump(mode="json"), True
    if args.command == "swap-bias":
        swaps = _Swaps.model_validate(decode_json(_read(args.pairs)))
        return evaluate_position_swap_bias(swaps.pairs).model_dump(mode="json"), True
    a, b, fixtures = _read(args.model_a), _read(args.model_b), _read(args.tests)
    # Validate every optional input before launching either candidate.
    spec = (
        IFEvalConstraintSpec.model_validate(decode_json(_read(args.constraints)))
        if args.constraints
        else None
    )
    calibration = _cohen(args.ratings) if args.ratings else None
    comparison = compare_code_candidates_ab(
        a,
        b,
        fixtures,
        ASTAnalysisPolicy(require_function_name=args.function),
        args.timeout,
    )
    report: dict[str, Any] = {"code_comparison": comparison.model_dump(mode="json")}
    passed = comparison.winner != "tie_both_fail"
    if spec is not None:
        checked_a, checked_b = (
            verify_instruction_following(a, spec),
            verify_instruction_following(b, spec),
        )
        report["instruction_following"] = {
            "model_a": checked_a.model_dump(mode="json"),
            "model_b": checked_b.model_dump(mode="json"),
        }
        passed &= checked_a.passed and checked_b.passed
    if calibration is not None:
        report["cohens_kappa"] = calibration
    return report, passed


def main(argv: list[str] | None = None) -> int:
    """Write a versioned JSON report; return 0 on success, 1 on failure, 2 on usage errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    ifeval = commands.add_parser("ifeval", help="Verify response text against JSON constraints")
    ifeval.add_argument("--response", required=True)
    ifeval.add_argument("--constraints", required=True)
    grade = commands.add_parser("grade-ab", help="Execute reviewed Python candidates and fixtures")
    for option in ("model-a", "model-b", "tests"):
        grade.add_argument(f"--{option}", required=True)
    grade.add_argument("--function")
    grade.add_argument("--timeout", type=float, default=2.5)
    grade.add_argument("--constraints", help="Optional constraints applied to both source texts")
    grade.add_argument("--ratings", help="Optional aligned categorical ratings for Cohen's kappa")
    for command in ("kappa", "fleiss"):
        commands.add_parser(command).add_argument("--ratings", required=True)
    commands.add_parser("swap-bias").add_argument("--pairs", required=True)
    args = parser.parse_args(argv)
    try:
        report, passed = _run(args)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        code = "invalid_schema" if isinstance(exc, ValidationError) else "invalid_input"
        message = (
            "Input does not match the expected schema"
            if isinstance(exc, ValidationError)
            else str(exc)
        )
        print(
            json.dumps(
                {"schema_version": 1, "error": {"code": code, "message": message}}, sort_keys=True
            )
        )
        return 1
    print(json.dumps({"schema_version": 1, "report": report}, sort_keys=True, allow_nan=False))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
