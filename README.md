# Vietnamese-English LLM Evaluation Toolkit

[![tests](https://github.com/ngovanduong-dev/vi-en-llm-evaluation-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/ngovanduong-dev/vi-en-llm-evaluation-toolkit/actions/workflows/tests.yml)

A small Python toolkit for working with Vietnamese-English LLM evaluation data.
It provides typed records for prompts, response pairs, rubric scores, and
evaluator judgments; validates JSONL datasets; calculates simple rubric
summaries; exports reports; and performs lightweight checks on coding responses.

The installed `vi-en-eval` command currently exposes JSONL validation. Scoring,
report export, and coding-response checks are available as Python APIs.

## What the Tool Does

- Models prompt, response-pair, and evaluation records with strict Pydantic
  schemas.
- Validates JSONL syntax, required fields, enum values, score ranges, non-blank
  text, extra fields, and duplicate record IDs.
- Calculates an average across seven rubric dimensions and assigns a simple
  qualitative score band.
- Normalizes common pairwise winner labels and builds compact evaluation
  summaries.
- Renders individual evaluations as Markdown and exports summary rows as CSV.
- Checks Python syntax and validates JSON or JSONL text without executing
  generated code.

The repository also includes reusable evaluation rubrics, sample datasets, and
a sample Markdown report.

## Installation

Python 3.11 or newer with `venv` support is required. From a checked-out copy
of the repository, create a virtual environment and install the package in
editable mode.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

POSIX shells:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## CLI Examples

Validate each bundled dataset against its registered schema:

```bash
vi-en-eval data/sample_prompts.jsonl --schema prompt
vi-en-eval data/sample_responses.jsonl --schema response
vi-en-eval data/sample_evaluations.jsonl --schema evaluation
```

Return a machine-readable validation result:

```bash
vi-en-eval data/sample_evaluations.jsonl --schema evaluation --json
```

The validator can also be invoked as a Python module:

```bash
python -m vi_en_eval.jsonl_validator data/sample_evaluations.jsonl --schema evaluation
```

The command exits with status `0` for a valid file and `1` when validation
issues are found.

## Main Data Models

The models are defined in
[`src/vi_en_eval/schemas.py`](src/vi_en_eval/schemas.py).

| Model | Purpose | Main fields |
| --- | --- | --- |
| `PromptRecord` | A prompt to evaluate | `id`, `language`, `task_type`, `prompt`, `expected_constraints` |
| `ResponsePairRecord` | Two responses to the same prompt | `id`, `prompt_id`, `response_a`, `response_b`, optional model labels |
| `EvaluationRecord` | A completed pairwise judgment | record references, language, task type, winner, rubric scores, issues, rationale |
| `RubricScores` | Scores from 1 to 5 across seven criteria | instruction following, correctness, completeness, clarity, language naturalness, formatting, safety |
| `DetectedIssue` | A problem noted during review | category, severity, description, optional suggested fix |

Languages are `Vietnamese`, `English`, or `Bilingual`. Task types cover general,
translation, coding, safety, reasoning, and localization work. Pairwise winners
are `A`, `B`, or `Tie`.

All models reject unknown fields. IDs and required text fields must contain at
least one non-whitespace character.

## Evaluation and Scoring Capabilities

Scoring helpers in
[`src/vi_en_eval/scoring.py`](src/vi_en_eval/scoring.py) currently provide:

- normalization of common winner labels such as `response a`, `model b`, and
  `draw`;
- an arithmetic mean across the seven rubric dimensions;
- compact summaries containing record references, winner, average score, score
  band, issue count, and rationale.

Average scores use these fixed bands:

| Average | Band |
| ---: | --- |
| 4.5 or higher | `strong` |
| 3.5 to less than 4.5 | `acceptable` |
| 2.5 to less than 3.5 | `weak` |
| Less than 2.5 | `poor` |

Report helpers in
[`src/vi_en_eval/report_exporter.py`](src/vi_en_eval/report_exporter.py) render
one evaluation as Markdown or export multiple evaluation summaries as CSV. A
sample output is available at
[`reports/sample_evaluation_report.md`](reports/sample_evaluation_report.md).

Lightweight coding-response checks in
[`src/vi_en_eval/code_checks.py`](src/vi_en_eval/code_checks.py) parse Python
syntax and validate JSON or JSONL text. The Markdown files in [`rubrics/`](rubrics/)
cover general responses, Vietnamese-English language QA, coding responses, and
prompt/rubric quality.

## Project Structure

```text
src/vi_en_eval/       Package schemas, validation, scoring, export, and checks.
data/                 Synthetic JSONL prompt, response, and evaluation records.
rubrics/              Human-readable evaluation rubrics.
reports/              Example report output.
portfolio_samples/    Additional human-readable synthetic review examples.
scripts/              Baseline inventory generator and checker.
artifacts/baseline/   Machine-readable inventory of the current repository state.
tests/                Pytest coverage for package and inventory behavior.
.github/workflows/    Continuous integration configuration.
```

## Data and Privacy

The bundled datasets, rubrics, reports, and examples use synthetic or otherwise
public-safe content. They do not contain private platform tasks, client data,
internal guidelines, paid task content, real model outputs, screenshots,
credentials, or work-queue material.

## Development and Testing

Install the development dependencies before running the full local checks:

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
ruff format --check --config "format.line-ending = 'auto'" .
mypy --strict src
bandit -c pyproject.toml -r src scripts
pip-audit --skip-editable
python -m build
python -B scripts/generate_baseline_inventory.py check
```

The local formatting command accepts the checkout's native line endings. CI
additionally enforces the repository's configured LF line endings.

The baseline artifact at
[`artifacts/baseline/current_state.json`](artifacts/baseline/current_state.json)
records the registered schemas, sample JSONL inventory, rubric and sample paths,
and collected tests. Regenerate it only when its tracked inputs change:

```bash
python -B scripts/generate_baseline_inventory.py generate
```

CI runs tests on Python 3.11, 3.12, and 3.13, then performs separate lint,
formatting, type-checking, security, sample-data validation, baseline, and build
checks.

## Limitations

- The CLI validates JSONL only; it does not run model inference, score model
  outputs, or export reports from the command line.
- Validation is per file. It does not check relationships between prompt,
  response-pair, and evaluation files.
- An evaluation stores one rubric-score set and one pairwise winner rather than
  separate criterion scores for both responses.
- Scoring is an unweighted average with fixed bands. There are no calibrated
  judges, agreement statistics, uncertainty estimates, or regression tests for
  model quality.
- Python checks parse syntax only. Generated code is never executed, tested, or
  sandboxed by this toolkit.
- The bundled records are small synthetic examples, not a representative
  benchmark or evidence of production model performance.

The project is licensed under the [MIT License](LICENSE).
