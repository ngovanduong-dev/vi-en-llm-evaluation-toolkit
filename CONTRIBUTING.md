# Contributing

Thank you for helping improve the Vietnamese-English LLM Evaluation Toolkit.
Review the current implementation and open public issues before proposing a
change.

## Before starting

1. Choose an existing public GitHub issue or open a focused issue before
   implementation.
2. Inspect the current implementation, tests, Git status, and relevant history.
3. Define the scope, non-goals, acceptance criteria, compatibility impact, and
   security or privacy risks.
4. State the validation plan before changing files.

Use a dedicated branch and keep one issue or tightly coupled vertical slice per
pull request. Do not mix unrelated cleanup with feature work.

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
Report exact commands and results, compatibility and migration impact,
security/privacy impact, known limitations, and unmet acceptance criteria.
Never mark work complete when a required check or acceptance criterion is
unmet.
