# Start Here — Vietnamese-English LLM Evaluation Lab

> Status: repository-local navigation and delivery guidance.

This repository currently contains a compact Python evaluation toolkit and an
NDA-safe synthetic portfolio. The documents introduced by GOV-001 define how
that implemented baseline can evolve into a professional, reproducible
evaluation lab without overstating current capabilities.

## Current and target status

- **CURRENT / IMPLEMENTED:** Pydantic records, JSON/JSONL validation, basic
  pairwise winner normalization and seven-dimension scoring, Markdown/CSV
  export, lightweight syntax/structured-output checks, synthetic samples,
  rubrics, tests, and GitHub Actions.
- **TARGET / PLANNED:** versioned benchmark and rubric registries, independent
  annotation, adjudication, agreement and calibration, reproducible
  experiments, restricted code evaluation, and agent-trajectory evaluation.
- **NOT YET IMPLEMENTED:** every target capability above unless repository code,
  tests, and generated evidence demonstrate otherwise.

## Read order

1. [`AGENTS.md`](../AGENTS.md)
2. [`CODEX_MASTER_CONTEXT.md`](../CODEX_MASTER_CONTEXT.md)
3. [`docs/00_PROJECT_CHARTER.md`](00_PROJECT_CHARTER.md)
4. [`docs/01_TARGET_ARCHITECTURE.md`](01_TARGET_ARCHITECTURE.md)
5. [`docs/02_ROADMAP_24_WEEKS.md`](02_ROADMAP_24_WEEKS.md)
6. The active issue in [`planning/BACKLOG.md`](../planning/BACKLOG.md)
7. The methodology/security documents referenced by that issue
8. Existing implementation, tests, Git status, and Git history

## Delivery horizon

- Default plan: 24 sequencing weeks at approximately 12–15 focused hours/week.
- An accelerated plan may parallelize independent work, but it must not remove
  benchmark pilots, independent annotation, adjudication, judge calibration,
  sandbox security review, or release audit gates.
- Work one issue or one tightly coupled vertical slice at a time.

Codex can accelerate implementation, tests, documentation, and repetitive
migration work. It cannot replace human judgment about construct validity,
difficult benchmark items, disagreement adjudication, or whether a metric
measures the intended behavior.

## Product direction

The target product identity is **Vietnamese-English LLM Evaluation Lab**: a
vendor-neutral, reproducible system for benchmark and rubric design, human
evaluation and adjudication, calibration, regression experiments, controlled
code and agent evaluation, and auditable reports.

That identity is a roadmap direction, not a statement that those systems are
already implemented.

## Working rule

Repository claims must be backed by code, tests, versioned data, or generated
artifacts. Never substitute inflated metrics, copied private content, or
decorative architecture for evidence.
