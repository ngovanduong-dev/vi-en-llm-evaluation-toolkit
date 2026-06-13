import csv

from src.report_exporter import evaluation_to_markdown, export_evaluations_csv, export_markdown_report
from src.schemas import EvaluationRecord


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


def test_evaluation_to_markdown_contains_core_sections():
    markdown = evaluation_to_markdown(sample_record())

    assert "# Evaluation Report: eval_report_001" in markdown
    assert "## Rubric Scores" in markdown
    assert "## Rationale" in markdown
    assert "Response A is more natural and complete." in markdown


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