# Vietnamese-English LLM Evaluation Toolkit & Synthetic Portfolio

[![tests](https://github.com/ngovanduong-dev/vi-en-llm-evaluation-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/ngovanduong-dev/vi-en-llm-evaluation-toolkit/actions/workflows/tests.yml)

This project demonstrates a synthetic AI training workflow: creating evaluation
records, validating JSONL datasets, scoring prompt-response pairs with rubrics,
reviewing Vietnamese-English language quality, checking coding-response issues,
and exporting reproducible evaluator reports.

All examples are synthetic and portfolio-safe. This repository does not contain
private platform tasks, internal guidelines, client data, paid task content,
real model outputs, screenshots, or work-queue materials.

## Who This Is For

For AI recruiters and platform reviewers, this repo provides readable synthetic
samples that show evaluator judgment, rationale writing, rubric design,
hallucination detection, localization QA, and technical response review.

For technical reviewers, it provides a small Python toolkit with Pydantic
schemas, JSONL validation, scoring helpers, report export, coding-response
checks, sample data, and pytest coverage.

## Reviewer Paths

For AI evaluation reviewers:

```text
README
-> portfolio_samples/README.md
-> selected synthetic sample
-> reports/sample_evaluation_report.md
```

For technical reviewers:

```text
README
-> src/
-> tests/
-> data/*.jsonl
-> rubrics/
-> reports/sample_evaluation_report.md
```

## Featured Portfolio Samples

The portfolio index is available at
[`portfolio_samples/README.md`](portfolio_samples/README.md).

Vietnamese-English response evaluation:

- [Response comparison](portfolio_samples/vi_en_response_evaluation/01_response_comparison.md)
- [Instruction-following review](portfolio_samples/vi_en_response_evaluation/02_instruction_following_review.md)
- [Hallucination detection review](portfolio_samples/vi_en_response_evaluation/03_hallucination_detection.md)
- [Vietnamese localization QA review](portfolio_samples/vi_en_response_evaluation/04_localization_qa_review.md)

Prompt and rubric writing:

- [Vietnamese long complex prompt](portfolio_samples/prompt_rubric_writing/01_vietnamese_long_complex_prompt.md)
- [Fine-grained rubric](portfolio_samples/prompt_rubric_writing/02_fine_grained_rubric.md)
- [Explicit vs implicit criteria](portfolio_samples/prompt_rubric_writing/03_explicit_vs_implicit_criteria.md)
- [Objective vs subjective criteria](portfolio_samples/prompt_rubric_writing/04_objective_vs_subjective_criteria.md)

Technical response review:

- [Python code review](portfolio_samples/technical_response_review/01_python_code_review.md)
- [SQL query review](portfolio_samples/technical_response_review/02_sql_query_review.md)
- [JSON output validation review](portfolio_samples/technical_response_review/03_json_output_validation.md)
- [REST API explanation review](portfolio_samples/technical_response_review/04_api_response_review.md)

## Toolkit Features

- Pydantic schemas for prompts, response pairs, rubric scores, detected issues,
  and evaluation records.
- Synthetic JSONL datasets for prompts, response pairs, and completed
  evaluations.
- JSONL validator for malformed lines, blank lines, schema errors, duplicate
  IDs, invalid winner labels, score ranges, and blank text fields.
- Rubric scoring helpers for winner normalization, average score calculation,
  score bands, and evaluation summaries.
- Markdown and CSV report export helpers.
- Coding-response checks for Python syntax, JSON text, and JSONL line validity.
- Rubrics for general response evaluation, Vietnamese-English language QA,
  coding response review, and prompt/rubric quality.
- Pytest coverage for the core validation, scoring, export, schema, and coding
  check behavior.
- GitHub Actions workflow for tests and sample JSONL validation on pull
  requests and pushes to `main`.

## Project Structure

```text
data/                 Synthetic JSONL records.
portfolio_samples/    Human-readable synthetic portfolio samples.
reports/              Sample exported evaluator report.
rubrics/              Public-safe evaluation rubrics.
src/                  Toolkit implementation modules.
tests/                Pytest coverage for core behavior.
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```

## JSONL Validation

Validate sample prompt, response, and evaluation datasets:

```bash
python -m src.jsonl_validator data/sample_prompts.jsonl --schema prompt
python -m src.jsonl_validator data/sample_responses.jsonl --schema response
python -m src.jsonl_validator data/sample_evaluations.jsonl --schema evaluation
```

Optional machine-readable output:

```bash
python -m src.jsonl_validator data/sample_evaluations.jsonl --schema evaluation --json
```

## Synthetic Dataset Format

Each evaluation record contains:

- `id`
- `prompt_id`
- `response_pair_id`
- `language`
- `task_type`
- `winner`
- `rubric_scores`
- `detected_issues`
- `rationale`

## Rubric Scoring

Scoring helpers live in [`src/scoring.py`](src/scoring.py). They support:

- Winner label normalization.
- Average rubric score calculation.
- Score-band summaries.
- Compact evaluation summary dictionaries for reporting.

## Report Export

Report helpers live in [`src/report_exporter.py`](src/report_exporter.py).

The sample Markdown report is available at
[`reports/sample_evaluation_report.md`](reports/sample_evaluation_report.md).

## Coding Response Checks

Coding checks live in [`src/code_checks.py`](src/code_checks.py). They support:

- Python syntax parsing with line and column diagnostics.
- JSON text validation.
- JSONL text validation with per-line results.
- A coding-review checklist for syntax errors, logic errors, missing edge
  cases, runtime risks, API misuse, unsupported claims, inefficient solutions,
  weak explanations, and invalid JSON output.

## What This Demonstrates

- Vietnamese-English LLM response evaluation.
- Rubric-based scoring and response ranking.
- Concise evaluator rationale writing.
- Hallucination and unsupported-claim detection.
- Vietnamese localization and tone QA.
- Prompt/rubric design with explicit, implicit, objective, and subjective
  criteria.
- Technical AI response review for Python, SQL, JSON, JSONL, and API
  explanations.
- JSONL validation and reproducible report generation.
- Confidentiality-safe public portfolio presentation.

## Current Status

The current repo is a toolkit plus synthetic portfolio. It includes code,
tests, GitHub Actions, sample JSONL data, rubrics, portfolio samples, and a
sample report.

Planned follow-up work includes a Streamlit comparison UI, README screenshots,
additional portfolio-safe documentation, and a release tag. Those items are not
claimed as complete yet.

## Confidentiality Note

All examples in this repository are synthetic, generalized, and public-safe.
They are designed to demonstrate AI evaluation skills without exposing private
platform tasks, internal guidelines, client materials, paid task prompts, real
model outputs, screenshots, work queues, or project codenames.
