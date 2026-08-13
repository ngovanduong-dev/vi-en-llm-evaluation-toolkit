"""Markdown and CSV export helpers for evaluation records."""

from __future__ import annotations

import csv
from pathlib import Path

from vi_en_eval.schemas import EvaluationRecord
from vi_en_eval.scoring import calculate_average_score, summarize_evaluation


def _detected_issue_lines(record: EvaluationRecord) -> list[str]:
    if not record.detected_issues:
        return ["- No major issues detected."]

    lines: list[str] = []
    for issue in record.detected_issues:
        lines.append(f"- **{issue.category}** ({issue.severity.value}): {issue.description}")
        if issue.suggested_fix:
            lines.append(f"  - Suggested fix: {issue.suggested_fix}")

    return lines


def evaluation_to_markdown(record: EvaluationRecord) -> str:
    """Render one evaluation record as Markdown."""

    lines = [
        f"# Evaluation Report: {record.id}",
        "",
        f"- Prompt ID: `{record.prompt_id}`",
        f"- Response Pair ID: `{record.response_pair_id}`",
        f"- Language: {record.language.value}",
        f"- Task Type: {record.task_type.value}",
        f"- Winner: {record.winner}",
        f"- Average Score: {calculate_average_score(record.rubric_scores)}",
        "",
        "## Rubric Scores",
        "",
        "| Criterion | Score |",
        "| --- | ---: |",
    ]

    for field, score in record.rubric_scores.model_dump().items():
        label = field.replace("_", " ").title()
        lines.append(f"| {label} | {score} |")

    lines.extend(["", "## Detected Issues", "", *_detected_issue_lines(record)])
    lines.extend(["", "## Rationale", "", record.rationale, ""])
    return "\n".join(lines)


def export_markdown_report(record: EvaluationRecord, path: str | Path) -> Path:
    """Write one evaluation report to a UTF-8 Markdown file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(evaluation_to_markdown(record), encoding="utf-8")
    return output_path


def export_evaluations_csv(records: list[EvaluationRecord], path: str | Path) -> Path:
    """Write compact evaluation summaries to a UTF-8 CSV file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id",
        "prompt_id",
        "response_pair_id",
        "language",
        "task_type",
        "winner",
        "average_score",
        "score_band",
        "issue_count",
        "rationale",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            writer.writerow(summarize_evaluation(record))

    return output_path
