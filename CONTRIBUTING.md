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

The repository currently uses `requirements.txt` and imports modules as
`src.*`. Packaging migration and additional quality tools are planned work and
must not be described as implemented.

```bash
python -m venv .venv
pip install -r requirements.txt
python -m pytest -q
python -m src.jsonl_validator data/sample_prompts.jsonl --schema prompt
python -m src.jsonl_validator data/sample_responses.jsonl --schema response
python -m src.jsonl_validator data/sample_evaluations.jsonl --schema evaluation
```

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
