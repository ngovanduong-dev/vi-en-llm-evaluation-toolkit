# Production-Style Code Evaluation

> Status: TARGET / PLANNED. Current code checks parse syntax and structured
> output only. They do not execute code and are not a sandbox.

## Threat model

Generated code may delete files, exhaust resources, exfiltrate over network,
read credentials, access host sockets, fork indefinitely, exploit dependencies,
modify tests, or fake expected output. Treat submissions as hostile.

## Task levels

1. **Function:** single function/file with property and hidden tests.
2. **Module:** multiple files, dependencies, static/type and regression checks.
3. **Repository patch:** issue, snapshot, patch application, suite, scope, logs.
4. **Service/concurrency:** database/service fixtures, authorization, races,
   idempotency, and performance.

Ship progressively; do not begin at level 4.

## Required sandbox policy

- OCI/Docker backend selected through a reviewed ADR;
- unprivileged user;
- outbound network disabled;
- read-only root filesystem where practical;
- isolated writable workdir;
- controlled input/output mounts;
- memory/CPU/PID/disk/wall-clock limits;
- pinned image digest;
- default seccomp and dropped capabilities;
- no Docker socket;
- deterministic locale/timezone;
- cleanup in `finally`.

## Target task package

```text
task/
  task.yaml
  prompt.md
  starter/
  public_tests/
  private_tests/
  oracle/
  fixtures/
  rubric.yaml
  task_card.md
```

## Validation before release

- starter fails the intended tests;
- gold and alternative valid solutions pass;
- known wrong solutions fail;
- tests are deterministic;
- requirements are visible in the prompt;
- limits are realistic;
- provenance/license is clear.

## Scoring

Preserve patch/application, parse/build, public/hidden/regression/security/
property-test, performance/resource, scope, explanation, and fatal-error
components. Justified hard failures override averages.

## Language progression

- Python: pytest, property tests, task-relevant Ruff/mypy, focused security and
  resource checks.
- JavaScript/TypeScript: Vitest, compiler where relevant, deterministic
  concurrency fixtures, and API-existence tests.
- SQL/PostgreSQL: disposable database, reset/rollback, result-table oracle, and
  null/boundary/duplicate/concurrency/authorization fixtures.

## Anti-tampering

Use immutable tests, hidden filenames where practical, test-directory hashes,
no network/package downloads, workspace-diff checks, test-modification
detection, and captured commands/file changes.
