"""Compare two technical evaluator datasets without executing response content."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from vi_en_eval.technical_dataset import (
    TechnicalDataset,
    TechnicalDatasetLoadResult,
    format_technical_dataset_result,
    load_technical_dataset,
)
from vi_en_eval.technical_models import PairwiseTechnicalEvaluation, TechnicalRubricScores

LABELS = ("A", "B", "Tie")


@dataclass(frozen=True)
class ComparisonIssue:
    """A comparison-specific failure, additional to loader diagnostics."""

    code: str
    message: str
    evaluator: Literal["a", "b"] | None = None
    response_pair_id: str | None = None
    evaluation_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgreementResult:
    """Validation evidence and, only for valid inputs, comparison results."""

    evaluator_a: TechnicalDatasetLoadResult
    evaluator_b: TechnicalDatasetLoadResult
    issues: tuple[ComparisonIssue, ...]
    comparison: dict[str, Any] | None

    @property
    def is_valid(self) -> bool:
        """Whether comparison was possible (including a valid empty overlap)."""
        return self.comparison is not None

    def to_dict(self) -> dict[str, Any]:
        """Return versioned output; source text is never serialized implicitly."""
        return {
            "schema_version": 1,
            "is_valid": self.is_valid,
            "validation": {
                "evaluator_a": self.evaluator_a.to_dict(),
                "evaluator_b": self.evaluator_b.to_dict(),
            },
            "comparison_issues": [asdict(issue) for issue in self.issues],
            "comparison": self.comparison,
        }


def _duplicate_pair_issues(
    dataset: TechnicalDataset, evaluator: Literal["a", "b"]
) -> list[ComparisonIssue]:
    ids_by_pair: dict[str, list[str]] = defaultdict(list)
    for evaluation in dataset.technical_evaluations:
        ids_by_pair[evaluation.response_pair_id].append(evaluation.id)
    return [
        ComparisonIssue(
            code="duplicate_pair_assessment",
            message="Multiple evaluations assess the same response pair",
            evaluator=evaluator,
            response_pair_id=pair_id,
            evaluation_ids=tuple(sorted(ids)),
        )
        for pair_id, ids in sorted(ids_by_pair.items())
        if len(ids) > 1
    ]


def _same_sources(a: TechnicalDataset, b: TechnicalDataset) -> bool:
    # The existing three-file loader reads the shared sources twice. Compare
    # complete typed source records to reject observed changes between reads.
    return {p.id: p for p in a.prompts} == {p.id: p for p in b.prompts} and {
        r.id: r for r in a.response_pairs
    } == {r.id: r for r in b.response_pairs}


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _matched_record(
    a: PairwiseTechnicalEvaluation,
    b: PairwiseTechnicalEvaluation,
    *,
    include_rationales: bool,
) -> dict[str, Any]:
    differences: dict[str, dict[str, int]] = {}
    for name, candidate_a, candidate_b in (
        ("candidate_a", a.candidate_a, b.candidate_a),
        ("candidate_b", a.candidate_b, b.candidate_b),
    ):
        differences[name] = {
            field: getattr(candidate_a.rubric_scores, field)
            - getattr(candidate_b.rubric_scores, field)
            for field in TechnicalRubricScores.model_fields
        }
    scores_agree = all(delta == 0 for scores in differences.values() for delta in scores.values())
    record: dict[str, Any] = {
        "response_pair_id": a.response_pair_id,
        "prompt_id": a.prompt_id,
        "evaluation_id_a": a.id,
        "evaluation_id_b": b.id,
        "winner_a": a.winner,
        "winner_b": b.winner,
        "winner_agrees": a.winner == b.winner,
        "scores_agree": scores_agree,
        "score_differences_a_minus_b": differences,
        "human_adjudication_recommended": a.winner != b.winner or not scores_agree,
    }
    if include_rationales:
        record["rationales"] = {
            name: {
                "overall": evaluation.rationale,
                "candidate_a": evaluation.candidate_a.rationale,
                "candidate_b": evaluation.candidate_b.rationale,
            }
            for name, evaluation in (("evaluator_a", a), ("evaluator_b", b))
        }
    return record


def _compare_validated(
    a: TechnicalDataset, b: TechnicalDataset, *, include_rationales: bool
) -> dict[str, Any]:
    # Call only after reference and uniqueness checks. No first/last-row policy.
    by_pair_a = {e.response_pair_id: e for e in a.technical_evaluations}
    by_pair_b = {e.response_pair_id: e for e in b.technical_evaluations}
    source_ids = {r.id for r in a.response_pairs}
    ids_a, ids_b = set(by_pair_a), set(by_pair_b)
    matched_ids = sorted(ids_a & ids_b)
    matched = [
        _matched_record(by_pair_a[p], by_pair_b[p], include_rationales=include_rationales)
        for p in matched_ids
    ]
    matrix = [[0 for _ in LABELS] for _ in LABELS]
    for pair_id in matched_ids:
        matrix[LABELS.index(by_pair_a[pair_id].winner)][
            LABELS.index(by_pair_b[pair_id].winner)
        ] += 1
    n = len(matched)
    agreements = sum(matrix[i][i] for i in range(3))
    row_totals = [sum(row) for row in matrix]
    column_totals = [sum(row[i] for row in matrix) for i in range(3)]
    expected_numerator = sum(row_totals[i] * column_totals[i] for i in range(3))
    # Integer arithmetic identifies degenerate marginals exactly and avoids
    # cancellation in (observed - expected) / (1 - expected).
    kappa_denominator = n * n - expected_numerator
    kappa = (n * agreements - expected_numerator) / kappa_denominator if kappa_denominator else None
    undefined_reason = (
        "no_matched_pairs"
        if n == 0
        else "expected_agreement_is_one"
        if not kappa_denominator
        else None
    )
    score_matches = sum(record["scores_agree"] for record in matched)
    return {
        "coverage": {
            "source_response_pairs": len(source_ids),
            "evaluator_a_evaluated_pairs": len(ids_a),
            "evaluator_b_evaluated_pairs": len(ids_b),
            "evaluator_a_coverage": _ratio(len(ids_a), len(source_ids)),
            "evaluator_b_coverage": _ratio(len(ids_b), len(source_ids)),
            "matched_pairs": n,
            "only_a_pair_ids": sorted(ids_a - ids_b),
            "only_b_pair_ids": sorted(ids_b - ids_a),
            "missing_a_pair_ids": sorted(source_ids - ids_a),
            "missing_b_pair_ids": sorted(source_ids - ids_b),
            "neither_pair_ids": sorted(source_ids - ids_a - ids_b),
        },
        "winner_agreement": {
            "labels": list(LABELS),
            "rows": "evaluator_a",
            "columns": "evaluator_b",
            "confusion_matrix": matrix,
            "matched_pairs": n,
            "agreements": agreements,
            "disagreements": n - agreements,
            "observed_agreement": _ratio(agreements, n),
            "expected_agreement": _ratio(expected_numerator, n * n),
            "cohens_kappa": kappa,
            "kappa_undefined_reason": undefined_reason,
        },
        "rubric_score_agreement": {
            "matched_pairs": n,
            "exact_match_pairs": score_matches,
            "exact_match_rate": _ratio(score_matches, n),
        },
        "matched_evaluations": matched,
    }


def compare_technical_evaluations(
    prompts_path: str | Path,
    response_pairs_path: str | Path,
    evaluations_a_path: str | Path,
    evaluations_b_path: str | Path,
    *,
    include_rationales: bool = False,
) -> AgreementResult:
    """Validate both inputs and compare by pair ID, never by row or evaluation ID.

    Incomplete coverage is valid and reported. Any invalid dataset or ambiguous
    pair assessment suppresses the entire comparison. Inputs must remain stable
    during loading. Rationales are opt-in and may contain sensitive quotations.
    """
    a = load_technical_dataset(prompts_path, response_pairs_path, evaluations_a_path)
    b = load_technical_dataset(prompts_path, response_pairs_path, evaluations_b_path)
    issues: list[ComparisonIssue] = []
    evaluators: tuple[tuple[Literal["a", "b"], TechnicalDatasetLoadResult], ...] = (
        ("a", a),
        ("b", b),
    )
    for name, loaded in evaluators:
        if loaded.dataset is not None:
            issues.extend(_duplicate_pair_issues(loaded.dataset, name))
    if a.dataset is None or b.dataset is None:
        return AgreementResult(a, b, tuple(issues), None)
    if not _same_sources(a.dataset, b.dataset):
        issues.append(
            ComparisonIssue("source_changed", "Shared source records changed between loads")
        )
    if issues:
        return AgreementResult(a, b, tuple(issues), None)
    return AgreementResult(
        a,
        b,
        (),
        _compare_validated(a.dataset, b.dataset, include_rationales=include_rationales),
    )


def format_agreement_result(result: AgreementResult) -> str:
    """Format concise coverage, agreement, and review guidance."""
    if result.comparison is None:
        lines = ["INVALID: evaluator comparison; no metrics computed"]
        for name, loaded in (("A", result.evaluator_a), ("B", result.evaluator_b)):
            if not loaded.is_valid:
                lines.extend([f"Evaluator {name}:", format_technical_dataset_result(loaded)])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in result.issues)
        return "\n".join(lines)
    comparison = result.comparison
    coverage, winner = comparison["coverage"], comparison["winner_agreement"]
    lines = [
        "VALID: evaluator comparison (agreement is not accuracy)",
        f"Source response pairs: {coverage['source_response_pairs']}",
        f"Evaluated: A={coverage['evaluator_a_evaluated_pairs']}, "
        f"B={coverage['evaluator_b_evaluated_pairs']}; matched={coverage['matched_pairs']}",
        f"Missing: A={len(coverage['missing_a_pair_ids'])}, "
        f"B={len(coverage['missing_b_pair_ids'])}",
        f"Winner agreements: {winner['agreements']}/{winner['matched_pairs']}; "
        f"exact agreement={winner['observed_agreement']}",
        f"Cohen's kappa: {winner['cohens_kappa']} "
        f"(undefined reason: {winner['kappa_undefined_reason']})",
        "Use --json for the confusion matrix, score differences, and pair IDs.",
        "Disagreements may need human adjudication; confidence is not calibrated.",
    ]
    return "\n".join(lines)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the comparison CLI parser."""
    parser = argparse.ArgumentParser(
        description="Inspect agreement between two technical evaluators."
    )
    parser.add_argument("--prompts", required=True, help="Shared prompt JSONL.")
    parser.add_argument("--responses", required=True, help="Shared response-pair JSONL.")
    parser.add_argument("--evaluations-a", required=True, help="Evaluator A technical JSONL.")
    parser.add_argument("--evaluations-b", required=True, help="Evaluator B technical JSONL.")
    parser.add_argument(
        "--json", action="store_true", help="Print versioned machine-readable JSON."
    )
    parser.add_argument(
        "--include-rationales",
        action="store_true",
        help="Include matched evaluator rationales in JSON (may contain sensitive text).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Return 0 for valid inputs, 1 for invalid inputs; argparse uses 2 for usage."""
    parser = create_argument_parser()
    args = parser.parse_args(argv)
    if args.include_rationales and not args.json:
        parser.error("--include-rationales requires --json")
    result = compare_technical_evaluations(
        args.prompts,
        args.responses,
        args.evaluations_a,
        args.evaluations_b,
        include_rationales=args.include_rationales,
    )
    if args.json:
        # JSON escapes preserve Unicode even when redirected stdout uses a
        # legacy Windows code page or ASCII. Consumers recover the exact text.
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=True, allow_nan=False))
    else:
        # Escape only unencodable characters without reconfiguring the caller's
        # stream. In-memory capture streams may have no encoding.
        encoding = sys.stdout.encoding or "utf-8"
        output = format_agreement_result(result)
        print(output.encode(encoding, errors="backslashreplace").decode(encoding))
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
