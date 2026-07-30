# Benchmark Design Standard

> Status: TARGET / PLANNED standard for benchmark issues. The current
> repository has synthetic samples but no versioned benchmark release.

## 1. Begin with the construct

Every future benchmark card must answer:

- What capability is measured?
- What is explicitly not measured?
- What decision will use the score?
- Who is the target user/model?
- Which failure modes matter?
- What evidence would invalidate the benchmark?

Valid constructs include preserving Vietnamese business register under explicit
constraints, detecting unsupported additions relative to evidence, resolving a
Python task under executable tests, and using tools while preserving
multi-turn constraints. “General intelligence” and “overall quality” are not
acceptable item-level constructs.

## 2. Item lifecycle

```text
draft -> author_review -> pilot -> revised -> gold_candidate
      -> adjudicated -> released -> deprecated
```

An item may become `defective` at any stage. Defective items remain auditable
but are excluded according to release policy.

## 3. Item requirements

Each item includes stable identity, construct/task family, input and
candidate/target, expected constraints, criterion mappings, evidence/oracle,
language/locale, difficulty, slices, provenance/license, contamination risk,
author/reviewer, rubric/benchmark version, gold status, rationale, and known
ambiguity.

## 4. Difficulty

- **easy:** one dominant explicit failure;
- **medium:** multiple constraints or one subtle issue;
- **hard:** plausible trade-off, partial correctness, evidence ambiguity, or
  trajectory reasoning;
- **challenge:** adversarial bias probe, rare slice, or disagreement-prone case.

Length alone does not make an item hard.

## 5. Pairwise composition

A mature set includes A wins, B wins, ties, both-bad outcomes, correctness/style
and completeness/concision trade-offs, factuality/utility trade-offs,
localized fluency/meaning conflicts, and low-confidence escalation cases.

Randomize display order. Gold labels use canonical identities, not screen
positions.

## 6. Rubric linkage

Criteria must be atomic, self-contained, observable, anchored, linked to prompt
constraints, classified by evaluator type, and marked hard/soft. Aggregation
policy is versioned; justified hard constraints may override averages.

## 7. Splits

Recommended target splits are `authoring`, `pilot`, `dev`, `public_test`,
`private_test`, `challenge`, and `regression`. Do not tune on private-test
outcomes or publish hidden answer keys.

## 8. Contamination controls

Record release dates and content hashes, check near duplicates, keep private or
dynamic components where practical, refresh temporal sets, track translated
relationships, and never claim “contamination-free” without evidence.

## 9. Quality review

Before release:

1. validate schemas and references;
2. run gold/oracle behavior;
3. inspect duplicates and slices;
4. obtain independent annotation;
5. adjudicate disagreements;
6. test rubric sensitivity and judge probes;
7. document defects/exclusions;
8. freeze the content hash.

## 10. Benchmark card

Include summary, intended/out-of-scope uses, construction, sources/licenses,
annotation, agreement/adjudication, metrics/uncertainty, contamination,
ethical/privacy considerations, limitations, version history, and
reproducibility commands.
