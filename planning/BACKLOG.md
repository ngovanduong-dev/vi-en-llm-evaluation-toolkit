# Execution Backlog

> Status: TARGET / PLANNED execution order. An issue ID in this document does
> not mean that capability is implemented.

Use IDs in order unless a dependency, security issue, or defect requires
documented reprioritization.

## M0 — Baseline and Governance

### GOV-001 Add durable project instructions

Scope:

- add reconciled repository-local governance, architecture, methodology,
  security, contribution, issue, and pull-request guidance;
- preserve current runtime behavior and README reviewer paths;
- clearly separate implemented and planned capabilities;
- exclude future v2 JSON schemas and distribution-only pack files.

Acceptance:

- all repository-local paths and relative Markdown links are valid;
- no unsupported current-state claim;
- no duplicate active pull-request template;
- full current tests and sample validators pass;
- no change under runtime, tests, data, rubrics, reports, or schema
  implementation.

### BASE-001 Generate baseline inventory

- Script counts schemas, JSONL records, portfolio samples, rubrics, and tests.
- Target artifact: `artifacts/baseline/current_state.json`.
- Acceptance: README metrics can consume generated values.

### BASE-002 Create claim-evidence matrix

- Map each current public claim to code, test, report, or unsupported status.
- Acceptance: unsupported items are not presented as implemented.

### ENG-001 Migrate packaging to pyproject

- Preserve `python -m pytest` and current module imports.
- Add documented editable install.

### ENG-002 Add lint, type, coverage, and pre-commit

- Add Ruff, mypy, coverage, and pre-commit.
- Choose thresholds after measuring baseline.
- Do not lower correctness to satisfy tooling.

### CI-001 Harden GitHub Actions

- Minimal permissions, deterministic matrix, caches, and artifact reports.
- No API keys required.

## M1 — Evaluation Core v2

- CORE-001 Define ID and version types.
- CORE-002 Define benchmark/rubric manifests.
- CORE-003 Define candidate and per-response score records.
- CORE-004 Define annotation confidence/evidence records.
- CORE-005 Define adjudication records preserving originals.
- CORE-006 Define experiment/run/result records.
- CORE-007 Export JSON schemas.
- DATA-001 Implement content hashing.
- DATA-002 Implement cross-file referential integrity.
- DATA-003 Implement duplicate/near-duplicate diagnostics.
- MIG-001 Build legacy-to-v2 migration.
- MIG-002 Add golden serialization and idempotence tests.
- CLI-001 Add dataset validate/inspect commands.
- CLI-002 Add rubric validate/inspect commands.
- CLI-003 Add migration dry-run and non-destructive output.
- DOC-001 Publish v2 data model and migration guide.

## M2 — Benchmark and Human Operations

- BENCH-001 Define benchmark/data card templates.
- BENCH-002 Define task/slice/difficulty taxonomy.
- BENCH-003 Define authoring and defect-review workflow.
- BENCH-004 Author a 20-item VI-EN preference pilot with A/B wins, ties,
  both-bad outcomes, and subtle trade-offs.
- BENCH-005 Add contamination/provenance/license checks.
- ANN-001 Implement randomized blind assignment.
- ANN-002 Implement independent annotation submission.
- ANN-003 Implement confidence/evidence/duration.
- ANN-004 Implement import/export and qualification mode.
- ADJ-001 Implement disagreement taxonomy.
- ADJ-002 Implement immutable adjudication queue/records.
- METRIC-001 Raw agreement and label distributions.
- METRIC-002 Cohen and weighted kappa.
- METRIC-003 Krippendorff alpha support.
- METRIC-004 Agreement slices and bootstrap intervals.
- PILOT-001 Run/document initial pilot.
- PILOT-002 Revise guidelines/items.
- PILOT-003 Run holdout recheck and freeze a rubric version.

## M3 — Calibration and Experiments

- EXP-001 Define provider-neutral `Target` protocol.
- EXP-002 Implement mock/replay target.
- EXP-003 Implement run manifest, item status, and artifact store.
- EXP-004 Implement cache identity and resumability.
- EVAL-001 Define evaluator/scorer protocol.
- EVAL-002 Implement deterministic graders.
- EVAL-003 Implement hard constraints and composites.
- EXP-005 Baseline/candidate paired comparison.
- STAT-001 Paired bootstrap confidence intervals.
- STAT-002 Slice aggregation and practical-effect policy.
- REG-001 Versioned regression policy.
- JUDGE-001 Optional model-judge adapter.
- JUDGE-002 Blind/order-swap and bias-probe suite.
- JUDGE-003 Confidence calibration and reliability report.
- JUDGE-004 Selective escalation/abstention.
- REPORT-001 Canonical JSON result bundle.
- REPORT-002 CSV/Markdown/HTML renderers.
- CI-002 Fast deterministic evaluation smoke suite.
- RELEASE-003 Publish v0.4 experiment/calibration evidence.

## M4 — Code Evaluation

- SEC-001 Code-evaluation threat model.
- SBX-001 Define sandbox protocol and typed result.
- SBX-002 Restricted backend with no network, non-root execution, and limits.
- SBX-003 Timeout, resource, cleanup, and log tests.
- SBX-004 Host-access and test-tampering negative tests.
- CODE-001 Code-task manifest and build validation.
- CODE-002 Python function-level harness.
- CODE-003 Hidden and property tests.
- CODE-004 Python patch/repository prototype.
- CODE-005 JavaScript/TypeScript Vitest harness.
- CODE-006 SQL/PostgreSQL harness.
- CODE-007 Gold/known-wrong/flakiness audit.
- REPORT-003 Code-evaluation report.

## M5 — Agent Evaluation

- AGENT-001 Trace/event schema.
- AGENT-002 Fixed local tool fixtures.
- AGENT-003 Trace persistence and replay.
- AGENT-004 Final-state outcome scorers.
- AGENT-005 Tool selection/argument/order scorers.
- AGENT-006 Recovery/repetition/efficiency scorers.
- AGENT-007 Policy and side-effect scanners.
- AGENT-008 Multi-turn constraint task suite.
- AGENT-009 Tool-failure and approval-boundary suite.
- AGENT-010 Agent comparison report.

## M6/M7 — Hardening and v1

- PROD-001 Production-trace import schema using synthetic/replay data.
- PROD-002 Sampling and failure-promotion workflow.
- SEC-002 Dependency/license/secrets audit.
- SEC-003 Final threat-model review.
- PERF-001 Performance and resource profiling.
- UI-001 Minimal viewer consuming stable result APIs.
- DOC-002 Architecture diagram and reviewer path.
- DOC-003 Complete benchmark/data/methodology/limitations documentation.
- PORT-001 Generate claim-evidence matrix and README proof block.
- AUDIT-001 Fresh-clone reproducibility audit.
- AUDIT-002 Independent methodology review checklist.
- RELEASE-100 v1.0.0 release.
