# Codex Session Prompts

These prompts assume repository-local files and the status vocabulary defined
in [`AGENTS.md`](../AGENTS.md).

## A. Start an implementation session

Read [`AGENTS.md`](../AGENTS.md),
[`CODEX_MASTER_CONTEXT.md`](../CODEX_MASTER_CONTEXT.md), the active milestone in
[`docs/02_ROADMAP_24_WEEKS.md`](../docs/02_ROADMAP_24_WEEKS.md), the assigned
issue in [`planning/BACKLOG.md`](BACKLOG.md), and referenced methodology files.
Inspect implementation and Git history before proposing changes. Restate
current state, objective, acceptance criteria, files, risks, and exact checks.
Implement only the smallest complete vertical slice. Report evidence and never
mark an unmet criterion complete.

## B. Architecture/design-only session

Do not modify files. Inspect current implementation relevant to the topic and
produce an ADR-quality design covering domain model, interfaces, data flow,
failure modes, migration, security/privacy, alternatives, and validation.
Prefer a reversible minimal design and identify assumptions it would change.

## C. Review a pull request

Review the diff against [`AGENTS.md`](../AGENTS.md), the assigned issue, and
milestone gate. Look for unsupported claims, provider coupling, missing
item-level evidence, statistical errors, lost original annotations, unsafe
execution, NDA risk, brittle tests, and scope growth. Run configured checks and
separate blockers from optional improvements.

## D. Benchmark authoring

Create only original NDA-safe items and follow
[`docs/03_BENCHMARK_DESIGN_STANDARD.md`](../docs/03_BENCHMARK_DESIGN_STANDARD.md).
Include real trade-offs, ties, both-bad cases, evidence/gold rationale, slices,
difficulty, provenance/license, and known ambiguity. Never reuse private tasks.

## E. Calibration analysis

Use frozen item-level labels and confidence. State sample size and missingness.
Compute raw agreement, the appropriate coefficient, calibration, selective
accuracy/coverage, paired intervals, and case-level errors. Do not generalize
beyond the sample.

## F. Code sandbox

Treat submissions as hostile. Read
[`docs/07_CODE_EVAL_PRODUCTION.md`](../docs/07_CODE_EVAL_PRODUCTION.md) and
[`docs/09_SECURITY_SANDBOX.md`](../docs/09_SECURITY_SANDBOX.md). Establish the
threat model, trust boundaries, and negative tests before implementation. Never
execute untrusted code on the host.

## G. Release audit

Use [`docs/12_DEFINITION_OF_DONE.md`](../docs/12_DEFINITION_OF_DONE.md). Verify
claims from evidence, reproduce commands, inspect cards, run implemented
restricted-execution and replay checks, review security/limitations, and list
blockers. Do not claim target capabilities that have not landed.
