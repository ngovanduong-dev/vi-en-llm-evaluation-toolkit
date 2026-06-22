# Vietnamese-English LLM Evaluation Toolkit

A lightweight Python toolkit for practicing and demonstrating LLM response
evaluation, bilingual QA, rubric-based scoring, coding-response review, and
JSON/JSONL validation.

## Purpose

This project simulates common AI training workflows:

- Compare two AI responses for the same prompt.
- Apply structured rubrics and select a winner.
- Write concise evaluator rationales.
- Review Vietnamese-English language quality and localization issues.
- Validate JSONL datasets before they are used for evaluation work.

## Portfolio Samples

The synthetic portfolio index lives in
[`portfolio_samples/README.md`](portfolio_samples/README.md). It defines the
planned human-readable sample categories that will complement the toolkit code,
tests, rubrics, JSONL data, and reports.

## Current Scope

The current milestone includes:

- Pydantic schemas for prompts, response pairs, rubric scores, detected issues,
  and evaluation records.
- Synthetic sample JSONL files.
- Rubric documents for general response evaluation, Vietnamese-English QA, and
  coding-response review.
- A JSONL validator that catches malformed lines, missing fields, invalid
  winner labels, score values outside 1-5, and empty rationales.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
python -m src.jsonl_validator data/sample_evaluations.jsonl --schema evaluation
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

## Confidentiality Note

All examples in this repository are synthetic. This project does not contain
private platform tasks, internal guidelines, client data, paid task content, or
screenshots from real work queues.
