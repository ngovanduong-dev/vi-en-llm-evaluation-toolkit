# Vietnamese-English LLM Evaluation Toolkit

[![tests](https://github.com/ngovanduong-dev/vi-en-llm-evaluation-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/ngovanduong-dev/vi-en-llm-evaluation-toolkit/actions/workflows/tests.yml)

A small Python toolkit for working with Vietnamese-English LLM evaluation data.
It provides typed records for prompts, response pairs, rubric scores, and
evaluator judgments; validates JSONL datasets; calculates simple rubric
summaries; exports reports; and performs lightweight checks on coding responses.

The installed `vi-en-eval` command currently exposes JSONL validation. Scoring,
report export, coding-response checks, and technical dataset-integrity checks
are available as Python APIs.

## What the Tool Does

- Models prompts, response pairs, legacy general judgments, and technical A/B
  assessments with Pydantic field constraints and unknown-field rejection.
- Validates JSONL syntax, required fields, enum values, score ranges, non-blank
  text, extra fields, and duplicate record IDs.
- Checks selected cross-record relationships for typed technical datasets through
  `validate_technical_dataset_integrity`.
- Calculates an average across seven legacy general rubric dimensions and assigns
  a descriptive qualitative band; this does not select the winner.
- Normalizes common pairwise winner labels and builds compact evaluation
  summaries.
- Renders legacy general evaluations as Markdown and exports their summary rows
  as CSV.
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

The legacy general models are defined in
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

Technical models in
[`src/vi_en_eval/technical_models.py`](src/vi_en_eval/technical_models.py) add:

| Model | Purpose |
| --- | --- |
| `TechnicalRubricScores` | Seven per-candidate dimensions: instruction following, correctness, edge-case handling, efficiency, maintainability, security/reliability, explanation quality |
| `TechnicalIssue` | One finding with a category, severity, description, and optional suggested fix |
| `CandidateTechnicalAssessment` | One candidate's scores, findings, and rationale |
| `PairwiseTechnicalEvaluation` | Separate A/B assessments, record references, A/B/Tie winner, confidence from 0 to 1, and overall rationale |

All models reject unknown fields. IDs and required text fields must contain at
least one non-whitespace character. These are individual-record structural and
type contracts, not semantic verification. Some fields, including rubric scores,
permit Pydantic coercion; this is not universally strict input typing.

The technical integrity API in
[`src/vi_en_eval/dataset_integrity.py`](src/vi_en_eval/dataset_integrity.py)
accepts sequences of typed prompts, response pairs, and technical evaluations.
It returns `DatasetIntegrityIssue` objects for duplicate IDs, missing references,
and prompt-reference mismatches. It skips mismatch inference for ambiguous
references to duplicate response-pair IDs. It does not load technical JSONL or
provide a technical CLI schema.

## Evaluation and Scoring Capabilities

Scoring helpers in
[`src/vi_en_eval/scoring.py`](src/vi_en_eval/scoring.py) currently provide:

- normalization of common winner labels such as `response a`, `model b`, and
  `draw`;
- an arithmetic mean across the seven rubric dimensions;
- compact summaries containing record references, winner, average score, score
  band, issue count, and rationale.

Legacy general scores have no candidate attribution: they are not separate A/B
scores or necessarily the winner's scores. Their mean summarizes stored numbers;
it does not establish groundedness or automatically determine the stored winner.
Technical assessments are candidate-specific and are not inputs to these general
scoring/export helpers. Rubric anchors and interpretation are documented in
[`rubrics/general_response_rubric.md`](rubrics/general_response_rubric.md) and
[`rubrics/coding_response_rubric.md`](rubrics/coding_response_rubric.md).

Average scores use these fixed descriptive bands:

| Average | Band |
| ---: | --- |
| 4.5 or higher | `strong` |
| 3.5 to less than 4.5 | `acceptable` |
| 2.5 to less than 3.5 | `weak` |
| Less than 2.5 | `poor` |

Report helpers in
[`src/vi_en_eval/report_exporter.py`](src/vi_en_eval/report_exporter.py) render
one legacy general evaluation as Markdown or export general summaries as CSV. A
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
tests/                Pytest coverage for package behavior.
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
ruff format --check .
mypy --strict src
bandit -c pyproject.toml -r src
pip-audit --skip-editable
python -m build
```

CI runs tests on Python 3.11, 3.12, and 3.13, then performs separate lint,
formatting, type-checking, security, sample-data validation, and build checks.

## Limitations

- The CLI validates JSONL only; it does not run model inference, score model
  outputs, or export reports from the command line.
- The CLI registers only `prompt`, `response`, and legacy `evaluation` schemas
  and validates files independently. Selected cross-record technical checks are
  available through the separate typed Python API described above.
- Legacy general judgments retain one pair-level score set without candidate
  attribution; technical judgments have separate A/B assessments. Historical
  general numbers cannot be reconstructed as candidate ratings when their
  original scoring basis is unknown.
- General score means and bands are descriptive. Technical evaluator confidence
  is stored, not calibrated. There are no calibrated judges, agreement statistics,
  statistical uncertainty estimates, or regression tests for model quality.
- Individual-record validation and technical relationship checks do not establish
  the truth of a rationale, correct rubric use, or a supported winner. Missing
  source evidence must be addressed in the judgment itself.
- Python checks use `ast.parse` only; successful AST construction does not prove
  compilation or runtime correctness. Generated code is never executed, tested,
  or sandboxed by the toolkit APIs or CLI.
- The bundled records are small synthetic examples, not a representative
  benchmark or evidence of production model performance.

The project is licensed under the [MIT License](LICENSE).
