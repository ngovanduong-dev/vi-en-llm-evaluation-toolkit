# Target Architecture

> Status: TARGET / PLANNED. This architecture is not the current module layout.

## Decision summary

Build an internal vendor-neutral evaluation kernel with optional adapters.
Adopt proven concepts—dataset, task/target, solver/agent, scorer/evaluator,
experiment, trace, report—without coupling the core to a hosted product.

## Component view

```text
                    +---------------------------+
                    | CLI / Python API / UI     |
                    +-------------+-------------+
                                  |
                    +-------------v-------------+
                    | Experiment Orchestrator   |
                    +---+----------+----------+-+
                        |          |          |
              +---------v--+ +-----v-----+ +--v-----------+
              | Targets     | | Evaluators| | Reporters    |
              | models/apps | | code/human| | md/json/html |
              +------+------+ +-----+-----+ +------+-------+
                     |              |              |
              +------v--------------v--------------v-------+
              | Domain + Registry + Artifact Store         |
              +---+----------------+---------------------+--+
                  |                |                     |
          +-------v------+ +-------v-------+ +-----------v----+
          | Benchmarks    | | Rubrics       | | Annotations    |
          | versions/hash | | versions/hash | | adjudication   |
          +--------------+ +---------------+ +----------------+
                                  |
                 +----------------v----------------+
                 | Sandboxes / Agent Tool Fixtures |
                 +---------------------------------+
```

## Planned modules

### `domain`

Immutable typed models, IDs, enums, result types, and validation errors. No
provider imports or file-system side effects.

### `datasets`

Manifest loading, split handling, provenance/license metadata, version/hash
calculation, referential integrity, and contamination metadata.

### `rubrics`

Criterion definitions, scale types, hard constraints, aggregation policies,
versioning, and compatibility checks.

### `annotations`

Assignment, independent submissions, confidence/evidence, disagreement
analysis, adjudication, and export.

### `evaluators`

Deterministic checks, imported human judgments, model-judge adapters, and
composites. Each produces typed criterion-level evidence, status, and
diagnostics.

### `experiments`

Target execution, caching, retries, run manifests, baseline/candidate pairing,
repetitions, resumability, and item status.

### `metrics`

Task metrics, agreement, calibration, uncertainty, slices, and regression
verdicts.

### `sandboxes`

Restricted code execution returning logs, resource use, timeout/security policy,
and controlled artifact paths.

### `agents`

Trace records, controlled tools, outcome and trajectory scorers, and scanners.

### `reports`

A stable machine-readable result bundle first, then Markdown/HTML rendering.
Every visual derives from the same result data.

### `adapters`

Optional translations for evaluation frameworks and model providers. Adapters
must not redefine the core.

## Planned data flow

1. Load benchmark and rubric manifests.
2. Validate versions, hashes, references, and policy.
3. Execute a target or ingest candidate outputs.
4. Persist raw output/trace before grading.
5. Apply deterministic evaluators.
6. Apply configured human/model evaluators.
7. Compute item, slice, calibration, and uncertainty metrics.
8. Compare to a baseline and regression policy.
9. Produce an immutable result bundle and human report.

## Storage strategy

### Phase 1

- JSONL/YAML source;
- SQLite index;
- local artifact directory;
- SHA-256 content identities.

### Phase 2

- optional Parquet result export;
- object-store adapter only if demonstrated need requires it.

Cloud infrastructure is not a baseline requirement.

## Target CLI examples

```bash
vi-eval dataset validate benchmarks/vi_en_preference
vi-eval rubric validate rubrics/vi_en_pairwise.yaml
vi-eval annotation import annotations/pilot.jsonl
vi-eval agreement report --benchmark vi_en_preference@0.2.0
vi-eval experiment run configs/experiments/baseline.yaml
vi-eval experiment compare <baseline-run> <candidate-run>
vi-eval judge calibrate configs/judges/judge-a.yaml
vi-eval code run benchmarks/python_code_eval --submission solution.py
vi-eval agent run benchmarks/agent_tasks --solver mock-agent
vi-eval report build <run-id>
```

These commands are illustrative and **NOT YET IMPLEMENTED**.

## API stability target

- pre-1.0 changes include migration notes;
- schemas include explicit versions;
- deprecated fields remain readable for at least one minor release where
  practical;
- serialization has golden-file tests;
- CLI errors are structured and actionable.

## ADRs required by later issues

1. package/build tool;
2. storage format and hashing;
3. schema migration strategy;
4. rubric aggregation;
5. provider-adapter boundary;
6. sandbox engine;
7. experiment cache identity;
8. hidden-test handling;
9. optional framework adapters.
