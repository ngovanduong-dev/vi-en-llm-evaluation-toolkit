import csv

from vi_en_eval.report_exporter import (
    evaluation_to_markdown,
    export_evaluations_csv,
    export_markdown_report,
)
from vi_en_eval.schemas import EvaluationRecord


def sample_record() -> EvaluationRecord:
    return EvaluationRecord.model_validate(
        {
            "id": "eval_report_001",
            "prompt_id": "prompt_001",
            "response_pair_id": "pair_001",
            "language": "Bilingual",
            "task_type": "Translation",
            "winner": "A",
            "rubric_scores": {
                "instruction_following": 5,
                "correctness": 5,
                "completeness": 4,
                "clarity": 5,
                "language_naturalness": 5,
                "formatting": 4,
                "safety": 5,
            },
            "detected_issues": [],
            "rationale": "Response A is more natural and complete.",
        }
    )


def sample_record_with_detected_issues() -> EvaluationRecord:
    return EvaluationRecord.model_validate(
        {
            "id": "eval_issue_001",
            "prompt_id": "prompt_001",
            "response_pair_id": "pair_001",
            "language": "Bilingual",
            "task_type": "Translation",
            "winner": "A",
            "rubric_scores": {
                "instruction_following": 5,
                "correctness": 5,
                "completeness": 4,
                "clarity": 5,
                "language_naturalness": 5,
                "formatting": 4,
                "safety": 5,
            },
            "detected_issues": [
                {
                    "category": "Tone",
                    "severity": "High",
                    "description": "Response B is too casual for the requested context.",
                    "suggested_fix": "Use a respectful academic tone.",
                },
                {
                    "category": "Missing constraint",
                    "severity": "Medium",
                    "description": "Response B does not preserve the requested deadline.",
                },
            ],
            "rationale": "Response A is safer and more complete.",
        }
    )


def test_evaluation_to_markdown_contains_core_sections():
    markdown = evaluation_to_markdown(sample_record())

    assert "# Evaluation Report: eval_report_001" in markdown
    assert "## Rubric Scores" in markdown
    assert "## Detected Issues" in markdown
    assert "## Rationale" in markdown
    assert "Response A is more natural and complete." in markdown


def test_evaluation_to_markdown_includes_detected_issue_categories():
    markdown = evaluation_to_markdown(sample_record_with_detected_issues())

    assert "**Tone** (High): Response B is too casual for the requested context." in markdown
    assert "Suggested fix: Use a respectful academic tone." in markdown
    assert (
        "**Missing constraint** (Medium): Response B does not preserve the requested deadline."
        in markdown
    )


def test_evaluation_to_markdown_handles_records_without_detected_issues():
    markdown = evaluation_to_markdown(sample_record())

    assert "- No major issues detected." in markdown


def test_export_markdown_report_writes_file(tmp_path):
    path = export_markdown_report(sample_record(), tmp_path / "report.md")

    assert path.exists()
    assert "eval_report_001" in path.read_text(encoding="utf-8")


def test_export_evaluations_csv_writes_summary_rows(tmp_path):
    path = export_evaluations_csv([sample_record()], tmp_path / "evaluations.csv")

    with path.open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["id"] == "eval_report_001"
    assert rows[0]["winner"] == "A"
    assert rows[0]["score_band"] == "strong"
