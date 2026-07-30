# Codex Master Context — Vietnamese-English LLM Evaluation Lab

**Status:** authoritative repository context

**Baseline commit:** `f3b377b19d2f2096d13dcf15347dfeca4d8e9856`

**Baseline date:** 2026-07-30

**Repository:** `ngovanduong-dev/vi-en-llm-evaluation-toolkit`

**Primary goal:** build credible public evidence for advanced multilingual
AI/LLM evaluation, benchmark, technical-review, and agent-evaluation roles.

Repository-local [`AGENTS.md`](AGENTS.md) is the operational authority.

## 1. CURRENT / IMPLEMENTED baseline

At the baseline commit, the repository is a compact Python toolkit plus an
NDA-safe synthetic portfolio. It contains:

- Pydantic records for prompts, response pairs, rubric scores, detected issues,
  and completed evaluations;
- strict model validation and JSONL diagnostics for malformed/blank lines,
  schema errors, duplicate IDs, invalid enums/ranges, and blank text;
- winner-label normalization and a simple average over seven rubric dimensions;
- Markdown and CSV export;
- lightweight Python-syntax, JSON, and JSONL checks;
- four public rubric documents;
- twelve human-readable synthetic portfolio samples;
- three JSONL files with nine bundled records;
- forty-four pytest cases collected from five test files at the baseline;
- GitHub Actions on the default branch for pytest and sample validation.

The baseline count above identifies a commit; it is not a claim that tests pass
forever. Run the documented checks against the current checkout before
reporting test status.

### Current strengths

- coherent Vietnamese-English evaluator positioning;
- clear synthetic-only and confidentiality boundaries;
- readable portfolio examples;
- tested structured-data validation and report helpers;
- separate recruiter and technical-reviewer paths in the README.

### Current limitations

- most examples are easy, obvious A-vs-B cases;
- the schema stores one aggregate rubric score set, not independent A/B scores;
- no annotation identity, confidence, evidence spans, rubric/dataset version,
  adjudication, provenance manifest, or experiment run model;
- no agreement analysis, calibration, uncertainty, or paired comparison;
- no experiment runner or provider-neutral target protocol;
- code checks parse syntax/format only and never execute submissions;
- no restricted sandbox;
- no agent trace or trajectory evaluation;
- no benchmark/data cards, threat model, release audit, or generated
  claim-evidence matrix;
- no UI, and UI must not precede core methodology and stable APIs.

## 2. TARGET / PLANNED product

The target is a vendor-neutral evaluation system that demonstrates the full
evaluation lifecycle:

1. define construct and intended use;
2. design benchmark tasks and rubrics;
3. record provenance, licensing, slices, and versions;
4. pilot with independent human annotation;
5. analyze disagreement and revise guidelines;
6. adjudicate while preserving original labels;
7. measure agreement and confidence calibration;
8. calibrate automated/LLM judges against human gold;
9. run reproducible baseline/candidate experiments;
10. compare paired outcomes with uncertainty and slice gates;
11. evaluate generated code inside restricted sandboxes;
12. evaluate agent final outcomes and trajectories;
13. sample production-like traces using synthetic or approved data;
14. publish auditable results, limitations, and release evidence.

None of these planned systems is implemented merely because it is documented.

## 3. Product identity and positioning

Preferred target name:

> **Vietnamese-English LLM Evaluation Lab**

Preferred target description:

> A reproducible evaluation lab for multilingual pairwise judgment, benchmark
> design, human adjudication, judge calibration, regression experiments,
> restricted code evaluation, and tool-using agent evaluation.

Until those capabilities exist, the README should continue to describe the
current product as a toolkit and synthetic portfolio.

The target differentiator is the intersection of Vietnamese-English
localization, human-feedback/rubric design, technical QA, executable evaluation,
and transparent statistical/governance practices.

## 4. TARGET architecture principles

### 4.1 Vendor neutrality

The repository should own a stable internal domain model. OpenAI Evals, Inspect
AI, LangSmith, provider SDKs, and other tools may be supported through optional
adapters.

### 4.2 Planned package layout

```text
src/vi_en_eval/
  domain/
  datasets/
  rubrics/
  annotations/
  evaluators/
  experiments/
  metrics/
  sandboxes/
  agents/
  reports/
  adapters/
  cli/
```

Supporting target directories:

```text
benchmarks/
configs/
docs/
artifacts/
```

The current `src.*` layout remains in place until its assigned migration issue
is implemented and tested.

### 4.3 Planned storage

Start with immutable JSONL/YAML sources, content hashes, a local artifact
directory, and SQLite metadata. Add Parquet or object-store adapters only when
demonstrated scale requires them. Do not add cloud infrastructure by default.

### 4.4 Planned protocols

- `DatasetRepository`
- `RubricRepository`
- `Target`
- `Evaluator`
- `Scorer`
- `Sandbox`
- `ExperimentStore`
- `ReportRenderer`

Provider-specific types must not leak into domain records.

## 5. TARGET canonical records

### Benchmark item

Planned fields include stable item/benchmark identity, benchmark and rubric
versions, language/task family, input and candidates/target, slices, difficulty,
provenance/license, author/review/gold status, contamination risk, timestamps,
and content hash.

### Pairwise annotation

Store independent criterion scores for responses A and B, criterion-level
preferences where applicable, `A`/`B`/`Tie`/`BothBad` overall preference,
major-error labels, evidence, confidence, rationale, duration, blinded display
metadata, annotator alias, and guideline/rubric versions.

### Adjudication

Preserve every original annotation, disagreement category, adjudicator
decision/evidence, rubric or guideline changes, gold status, confidence, and
escalation notes. Never overwrite first-pass labels.

### Experiment run

Planned identity includes run/baseline relation, Git SHA, dataset/rubric hashes,
target/model/provider snapshot, prompt/config/tool hashes, sampling settings,
sandbox policy/image, timings, outputs/traces, usage/cost, evaluator versions,
item/slice metrics, confidence intervals, and incomplete/failure status.

### Agent trace

Planned traces preserve messages, tool calls/arguments/results/errors,
timestamps, state changes, approvals, sandbox/network events, final output,
usage/cost, policy flags, and trace hash.

## 6. TARGET benchmark portfolio

The planned v1 benchmark family contains:

1. VI-EN Preference Challenge;
2. Vietnamese Localization QA;
3. Evidence-Grounded Factuality;
4. Rubric and Prompt Quality;
5. Technical Response Evaluation;
6. Multi-Turn and Agent Evaluation.

Mature suites should combine straightforward quality-control items, moderate
trade-offs, difficult/adversarial items, ties, both-bad outcomes, and known
disagreement probes. Difficulty must follow a documented construct rather than
length or artificial ambiguity.

## 7. TARGET human annotation and disagreement

The planned workflow writes an annotation guide, runs at least two independent
first passes where a human study is claimed, blinds identities, randomizes
order, collects evidence/confidence/time, measures appropriate agreement,
analyzes disagreement, revises guidelines, rechecks a holdout, freezes the
rubric, and adjudicates a gold subset.

Use raw agreement plus scale/design-appropriate coefficients. Explain sample
size, prevalence, missingness, slices, uncertainty, and low-agreement cases.
Never present single-person simulated labels as a multi-human study.

## 8. TARGET judge calibration

An LLM judge is an evaluator under test, not an oracle. Planned controls include
blinding, order randomization, swap consistency, style/verbosity perturbations,
identical-answer checks, separate calibration data, human-adjudicated gold,
confidence calibration, selective escalation, latency, and cost.

## 9. TARGET experiments and regression

Planned offline execution registers immutable dataset/rubric versions, runs
baseline and candidate on the same items, saves raw outputs/traces, applies
deterministic graders before human/model judgment, computes item/slice metrics
and paired intervals, then applies a versioned regression policy.

A higher overall mean alone cannot pass a candidate. Critical safety/security
slices, format/error rates, practical effect, cost, latency, and incomplete
items require explicit policy.

## 10. TARGET code evaluation

Planned code evaluation progresses from Python functions to modules/repository
patches, then JavaScript/TypeScript and SQL where justified. It evaluates
parse/build status, public and hidden behavior, regressions, edge cases,
security, resources, scope, and explanations.

Submissions must be treated as hostile and executed only inside a reviewed
restricted sandbox. The current `src/code_checks.py` is a parser and does not
provide this capability.

## 11. TARGET agent evaluation

Planned agent evaluation separates final outcome from trajectory. It evaluates
final state, constraints, side effects, tool choice and arguments, ordering,
recovery, unnecessary actions, policy behavior, cost, latency, and steps using
controlled offline fixtures.

The current repository has no agent runtime, agent trace schema, or agent
evaluation capability.

## 12. Security, governance, and audit

Maintain current project instructions, a risk register, data/NDA policy,
security reporting guidance, dependency/license inventory as it is introduced,
threat models for executable features, release checklists, and explicit
limitations. Public claims must map to repository evidence.

## 13. Milestones

- **M0 — Baseline and governance:** durable documents, baseline inventory,
  claim review, packaging/tooling foundation, preserved behavior.
- **M1 — Evaluation Core v2:** versioned records, manifests, integrity,
  migration, stable CLI.
- **M2 — Benchmark and Human Operations:** challenge pilot, annotation,
  disagreement, adjudication, agreement.
- **M3 — Calibration and Experiments:** judge calibration, run manifests,
  paired uncertainty, regression gates, reports.
- **M4 — Production-Style Code Evaluation:** threat model, restricted sandbox,
  audited language harnesses.
- **M5 — Agent Evaluation:** trace/replay, controlled tools, outcome and
  trajectory scoring.
- **M6/M7 — Hardening and v1 audit:** security/performance review, stable
  reviewer experience, claim evidence, independent reproduction.

See [`docs/02_ROADMAP_24_WEEKS.md`](docs/02_ROADMAP_24_WEEKS.md) and
[`planning/BACKLOG.md`](planning/BACKLOG.md).

## 14. Definition of target success

A v1 reviewer should be able to install cleanly, validate a versioned
benchmark, run a deterministic experiment, compare baseline/candidate with
item/slice uncertainty, inspect disagreement/adjudication and judge
calibration, run restricted code and controlled agent tasks, verify public
claims, and understand limitations/security boundaries.

These are v1 success criteria, not current capabilities.

## 15. Immediate sequence

Do not begin with Streamlit or UI.

1. finish governance and establish a reproducible baseline;
2. migrate packaging and quality tooling under their own issues;
3. define and migrate versioned schemas;
4. add integrity, manifests, and hashes;
5. build a difficult pairwise pilot and annotation/adjudication records;
6. implement agreement and calibration;
7. implement experiments and reports;
8. implement sandbox/code evaluation, then agent evaluation;
9. add UI only after stable core APIs and result bundles.

Use [`planning/BACKLOG.md`](planning/BACKLOG.md) as the execution source.
