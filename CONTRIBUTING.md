# Contributing

Thank you for helping improve the Vietnamese-English LLM Evaluation Toolkit.

## Before starting

Review the relevant code and tests, and check existing issues before making a
change. Work on a focused branch and keep each contribution limited to one
clear change. Avoid mixing unrelated cleanup with a feature or bug fix.

## Current development setup

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
ruff format --check .
mypy --strict src
bandit -c pyproject.toml -r src
pip-audit --skip-editable
python -m build
vi-en-eval data/sample_prompts.jsonl --schema prompt
vi-en-eval data/sample_responses.jsonl --schema response
vi-en-eval data/sample_evaluations.jsonl --schema evaluation
```

The audit skips only the editable, unpublished project itself; all installed
third-party runtime and development dependencies remain in scope.

On Windows, activate the environment with `.venv\Scripts\activate`. On POSIX
shells, use `source .venv/bin/activate`.

## Content and data

- Add only original synthetic material, procedurally generated material, or
  permissively licensed public data with recorded provenance.
- Never add private paid AI platform tasks, client data, private prompts,
  outputs, rubrics, screenshots, queue metadata, credentials, or personal data.
- Keep private data under `data/private/` and local artifacts under
  `artifacts/local/`; both paths are ignored.
- Label simulated, synthetic, pilot, experimental, and production-derived data
  accurately.

## Pull requests

Use [`.github/pull_request_template.md`](.github/pull_request_template.md).
Summarize what changed and why, and list the validation commands you ran with
their results. Use the optional notes section for compatibility, security,
limitations, or follow-up information when it is relevant.
