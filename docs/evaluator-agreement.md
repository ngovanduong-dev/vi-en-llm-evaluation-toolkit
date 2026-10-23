# Evaluator Agreement & Disagreement Inspector

`vi-en-compare` compares two sets of technical judgments against one shared set
of prompts and response pairs. It reports coverage, categorical winner agreement,
unweighted Cohen's kappa, and separate rubric-score differences. It never runs
candidate code or calls a model/API. No additional dependency is required.

## Installation and entry points

From a clone, use Python 3.11+ and `python -m pip install -e .` in a virtual
environment (see the [README](../README.md#installation)). Both entry points work:

```bash
vi-en-compare --prompts prompts.jsonl --responses responses.jsonl --evaluations-a evaluator_a.jsonl --evaluations-b evaluator_b.jsonl --json
python -m vi_en_eval.agreement --prompts prompts.jsonl --responses responses.jsonl --evaluations-a evaluator_a.jsonl --evaluations-b evaluator_b.jsonl
```

Without `--json`, output is a concise coverage/agreement summary. With `--json`,
stdout is one versioned JSON object. Exit codes follow the existing CLIs:

| Code | Meaning |
| --- | --- |
| `0` | Valid inputs, including partial coverage, empty overlap, or undefined kappa |
| `1` | Read, UTF-8, JSON, schema, reference, duplicate, or changed-source failure; no metrics |
| `2` | Invalid CLI usage; argparse diagnostic on stderr |

An exit code of zero is not an agreement threshold or a quality verdict.

Python callers can use:

```python
from vi_en_eval.agreement import compare_technical_evaluations

result = compare_technical_evaluations(
    "prompts.jsonl", "responses.jsonl", "evaluator_a.jsonl", "evaluator_b.jsonl"
)
report = result.to_dict()
assert report["schema_version"] == 1
```

## Input contract

- All four inputs are UTF-8 JSONL. Prompts use `PromptRecord`, responses use
  `ResponsePairRecord`, and both evaluation files use
  `PairwiseTechnicalEvaluation`. Legacy `EvaluationRecord` files do not fit this
  workflow. Empty files are allowed; blank physical lines are invalid.
- Each evaluator is loaded independently through `load_technical_dataset` with
  the same source paths. Strict JSON policy, field constraints, duplicate-ID
  checks, relationship validation, and diagnostic ordering are preserved.
  Integrity checks remain skipped after file-level failures.
- Each evaluation must link to an existing pair and the same prompt as that
  pair. No scores or statistics are computed if either dataset is invalid.
- Within each evaluator there may be **at most one evaluation per response
  pair**, even if assessments with different IDs contain identical judgments.
  Ambiguous pairs invalidate the entire comparison. This is an additional
  comparison constraint; existing dataset-loader behavior is unchanged.
- Pair identity is the exact, case-sensitive `response_pair_id`, never the line
  number or evaluation record ID. Evaluation IDs need only be unique within
  their own file; IDs shared across the two files do not imply identity.
- Missing assessments are allowed and reported, including source pairs assessed
  by neither evaluator. Unmatched assessments are excluded from every agreement
  denominator. Source prompts with no response pairs are not coverage units.
- Both evaluators must have judged the same source revision, candidate A/B order,
  and rubric interpretation. The tool checks links against the supplied source;
  the schema cannot prove historical provenance, independence, blindness, or
  rubric-version equivalence. No automatic candidate-order remapping occurs.
- Keep input files unchanged during the run. The shared sources are loaded twice;
  differing typed source records produce `source_changed`. This is not a file
  lock or an atomic snapshot guarantee. Files and output are held in memory;
  this workflow inherits the loader's standard-library parsing/resource limits.

## JSON report, schema version 1

| Top-level field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`, identifying this report contract |
| `is_valid` | Both datasets and comparison constraints passed |
| `validation.evaluator_a`, `.evaluator_b` | Existing loader reports: `is_valid`, `integrity_checked`, `files`, `issues` |
| `comparison_issues` | Additional failures, ordered by evaluator A then B, then pair ID; changed-source error last |
| `comparison` | Comparison object below, or `null` on any invalid input |

Each comparison issue contains `code`, `message`, `evaluator` (`a`, `b`, or
`null`), `response_pair_id` (or `null`), and `evaluation_ids` (sorted IDs, empty
when not applicable). Codes are `duplicate_pair_assessment` and `source_changed`.
Pair-uniqueness checks run only for datasets available after loader validation;
an invalid file is never partially salvaged. Loader `is_valid: true` can coexist
with report `is_valid: false` when comparison-specific constraints fail.

The comparison object contains:

| Field | Meaning |
| --- | --- |
| `coverage.source_response_pairs` | Total unique pairs in the shared source |
| `coverage.evaluator_a_evaluated_pairs`, `.evaluator_b_evaluated_pairs` | Valid assessed pair counts for each evaluator |
| `coverage.evaluator_a_coverage`, `.evaluator_b_coverage` | Assessed pairs / source pairs; `null` with zero source pairs |
| `coverage.matched_pairs` | Intersection count |
| `coverage.only_a_pair_ids`, `.only_b_pair_ids` | Pairs assessed by just one evaluator |
| `coverage.missing_a_pair_ids`, `.missing_b_pair_ids` | Source pairs lacking that evaluator's assessment |
| `coverage.neither_pair_ids` | Source pairs assessed by neither evaluator |
| `winner_agreement.labels` | Always `["A", "B", "Tie"]` |
| `winner_agreement.rows`, `.columns` | Always `evaluator_a` and `evaluator_b`, respectively |
| `winner_agreement.confusion_matrix` | 3x3 integer counts in `labels` order, matched population only |
| `winner_agreement.matched_pairs` | Winner agreement denominator |
| `winner_agreement.agreements`, `.disagreements` | Equal / different stored winner counts |
| `winner_agreement.observed_agreement` | Exact winner agreement fraction, or `null` for no matches |
| `winner_agreement.expected_agreement` | Chance-expected fraction from matched marginals, or `null` for no matches |
| `winner_agreement.cohens_kappa` | Unweighted categorical Cohen's kappa, or `null` when undefined |
| `winner_agreement.kappa_undefined_reason` | `no_matched_pairs`, `expected_agreement_is_one`, or `null` |
| `rubric_score_agreement.matched_pairs` | Score agreement denominator |
| `rubric_score_agreement.exact_match_pairs`, `.exact_match_rate` | Pairs with all 14 candidate/dimension scores equal; rate is `null` for no matches |
| `matched_evaluations` | All matched pairs in lexicographic pair-ID order, including agreements |

Each matched record contains:

- `response_pair_id`, `prompt_id`, `evaluation_id_a`, `evaluation_id_b` for
  traceability back to the input files.
- `winner_a`, `winner_b`, `winner_agrees`, and `scores_agree`.
- `score_differences_a_minus_b`: `candidate_a` and `candidate_b` objects, each
  containing all seven named technical dimensions. Values are **evaluator A's
  score minus evaluator B's score for the same candidate**, integers from -4 to
  4. These are descriptive score-step differences, not an interval-scale
  reliability statistic. The tool does not infer winners from scores or average
  across dimensions.
- `human_adjudication_recommended`: true when either the winner or any score
  differs. This is a review flag, not an automatic verdict that someone is wrong.
- Optional `rationales`, described below.

Select winner disagreements with `winner_agrees == false`, or all review cases
with `human_adjudication_recommended == true`. Even perfect winner agreement can
coexist with score disagreement. Issue descriptions, confidence values, and
differences between rationales are not compared.

All ID lists are lexicographically sorted. Valid output is invariant to input
row ordering for the same paths and records. Invalid file diagnostics retain
physical line numbers and therefore can change when invalid rows move. Paths
are reported as supplied through the existing loader; no timestamps or random
identifiers are added. Numbers are JSON numbers; undefined values are `null`,
never `NaN` or an arbitrary zero. CLI JSON uses lossless Unicode escapes so
Vietnamese text and identifiers also work with redirected ASCII/legacy-code-page
stdout. JSON decoding recovers the original Unicode strings.

## Rationales and privacy

Default reports omit prompt text, candidate response text, rationales, issue
descriptions, and model labels. They retain paths, IDs, score differences, and
existing validation diagnostics. This is content minimization, not anonymization:
IDs, paths, and invalid extra-field names may themselves contain sensitive text.

Use the evaluation IDs to inspect the original records locally. To include
matched rationales explicitly, add **both** `--json --include-rationales` (or
`include_rationales=True` in Python). Every matched record then includes
`rationales.evaluator_a` and `.evaluator_b`, each with `overall`, `candidate_a`,
and `candidate_b` strings. Rationales may quote private source content. Response
and prompt fields are still omitted. Invalid input never produces rationales.
Unmatched rationales remain accessible in the source evaluation files.

## Statistics and interpretation

Let `M[i][j]` be the confusion matrix, `n` its total count, `d` its diagonal sum,
and `r_i` and `c_i` its row and column totals. On matched pairs only:

```text
p_o = d / n
p_e = sum(r_i * c_i) / n^2
kappa = (p_o - p_e) / (1 - p_e)
```

This is ordinary, unweighted Cohen's kappa for nominal labels. The definition
and empirical-marginal chance model are also documented in
[scikit-learn's metric reference](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html);
scikit-learn is not a dependency. The implementation uses equivalent integer
count arithmetic before division to identify degenerate cases exactly.

If `n = 0`, both fractions and kappa are undefined. If `p_e = 1`, kappa is
undefined even though observed agreement is 1 (both evaluators use only the
same label). Constant but different labels have `p_e = 0`, agreement 0, and
kappa 0. Negative kappa is legitimate. `Tie` is a third label, not an abstention
or missing value. No ordinal distance between A, B, and Tie is assumed.

Agreement is not ground-truth accuracy. Shared mistakes can yield perfect
agreement, and majority preference does not establish correctness. Stored
confidence is not calibrated probability and has no effect on these metrics.
Missingness can bias the matched population. Kappa is sensitive to label
prevalence; inspect the matrix, coverage, score differences, and source evidence
together. No reliability threshold, significance test, or population claim is
provided. Weighted/multiple-rater measures, uncertainty intervals, confidence
calibration, gold-label accuracy, and adjudication storage are future work and
require their own methodological contracts.

## Reproducible synthetic example

The four files in [`data/agreement_example`](../data/agreement_example) contain
deliberately simulated labels and scores for arithmetic checks. They are not
independent human annotations or evidence of evaluator reliability. Repeated
simple response text is inert and judgments are intentionally not presented as
substantive technical assessments.

Run from the repository root (the single line works in PowerShell and POSIX):

```bash
vi-en-compare --prompts data/agreement_example/prompts.jsonl --responses data/agreement_example/response_pairs.jsonl --evaluations-a data/agreement_example/evaluations_a.jsonl --evaluations-b data/agreement_example/evaluations_b.jsonl --json
```

Expected coverage: 9 source pairs, 7 evaluated by each evaluator, 6 matched,
`pair-7` only in A, `pair-8` only in B, `pair-9` in neither. Each evaluator's
coverage is `7/9`. Matched labels are:

| Pair | Evaluator A | Evaluator B |
| --- | --- | --- |
| pair-1 | A | A |
| pair-2 | A | A |
| pair-3 | A | B |
| pair-4 | B | B |
| pair-5 | Tie | A |
| pair-6 | Tie | Tie |

The matrix is `[[2,1,0],[0,1,0],[1,0,1]]`. Its row totals are `(3,1,2)` and
column totals `(3,2,1)`. Thus `p_o = 4/6`, `p_e = (9+2+2)/36 = 13/36`, and
`kappa = 11/23`, approximately `0.4782608695652174`. Five matched pairs have all
14 scores equal. `pair-1` has the same winner but a +1 correctness-score
difference for candidate A, so it also receives the human-review flag.

Reproduce the arithmetic, invalid-input, privacy, and CLI tests with:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_agreement.py --no-cov
```
