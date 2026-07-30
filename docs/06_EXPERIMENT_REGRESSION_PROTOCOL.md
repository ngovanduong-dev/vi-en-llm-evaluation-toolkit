# Experiment and Regression Protocol

> Status: TARGET / PLANNED protocol. No experiment engine or regression policy
> is implemented in the current repository.

## Experiment identity

A planned experiment identity is derived from target code/config, Git SHA,
benchmark and rubric hashes, prompt/tool config, provider/model snapshot,
sampling settings, sandbox policy/image, and evaluator versions. Any change
creates a distinct run identity.

## Run lifecycle

```text
created -> validating -> running -> grading -> aggregating
        -> completed | partial | failed | canceled
```

Partial results are retained and never presented as complete.

## Required target artifacts

```text
run/
  manifest.json
  items.jsonl
  outputs/
  traces/
  evaluator_results.jsonl
  metrics.json
  comparisons.json
  report.md
  logs/
```

This layout is planned and is not present today.

## Target protocol

A target receives a typed item and returns output, trace, model/tool metadata,
usage, latency, and status/error. Planned implementations include replay,
callable, provider-adapter, and agent targets.

## Evaluator order

1. schema/format validation;
2. executable/deterministic checks;
3. reference-based metrics;
4. model judge;
5. human review/import;
6. composite aggregation.

A failed evaluator is not the same as a failed sample.

## Baseline comparison

Require the same benchmark version, item IDs, metric definitions, paired
analysis, explicit missing-item handling, and separate critical-slice results.

## CI modes

### Fast pull-request mode

Use a small deterministic regression set, mock/replay target, restricted code
smoke tests after the sandbox exists, and no paid APIs.

### Scheduled/release mode

Use the full public benchmark, optional provider runs, repeated stochastic
runs, judge calibration, and complete reports.

## Failure promotion

A failure may become an item only after confidentiality review, minimization or
synthetic recreation, provenance, authoring/review, rubric/gold validation, and
versioned release.

## Reporting

Report what changed; benchmark/rubric/target/config identity; item counts and
status; overall and slice metrics; paired effect/uncertainty; critical failures;
latency/cost; judge/human source; limitations; and reproduction commands.
