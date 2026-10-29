# Deterministic verification and calibration

`vi-en-grade` adds versioned JSON reports without changing `vi-en-eval`,
`vi-en-dataset`, or `vi-en-compare`. It is also available through
`python -m vi_en_eval.cli`. All input files use UTF-8.

## Response constraints

Save the following as `constraints.json`:

```json
{
  "require_unicode_nfc": true,
  "min_words": 2,
  "max_words": 100,
  "exact_bullet_count": 2,
  "required_keywords": ["Đà Nẵng"],
  "forbidden_phrases": ["unsupported claim"],
  "require_markdown_table": false,
  "require_valid_json_block": false,
  "required_json_keys": []
}
```

```bash
vi-en-grade ifeval --response response.txt --constraints constraints.json
```

Only NFC is enabled by default. Length bounds must be positive and ordered;
constraint terms must not be blank. The implementation compares the original
response with NFC, then normalizes a copy for lexical checks. Keywords and
forbidden phrases use case-folded substring matching, not whole-word matching.
An NFD response can therefore fail normalization while still satisfying a
Vietnamese keyword constraint.

Word count is the number of Unicode `\b\w+\b` matches in normalized text,
including code and punctuation-delimited tokens. This is not Vietnamese lexical
segmentation: `Đà Nẵng` counts as two tokens. Bullets are nonempty lines beginning
with `-`, `*`, `+`, `•`, or a number followed by `.` or `)`. Complete triple-backtick
fences are excluded from bullet and table checks. This intentionally supports a
small Markdown subset; nested fence variants, escaped table pipes, and full
CommonMark parsing are outside its contract.

A table needs a nonempty header and an immediately following separator with
matching column counts and at least one pipe. Separator cells contain at least
three hyphens and optional alignment colons. A separator alone does not pass.

JSON accepts one complete unlabelled or `json` triple-backtick block, or a whole
response containing raw JSON. More than one eligible block is ambiguous and
fails. Parsing uses the existing duplicate-name and non-finite-literal rejection
policy. Required keys refer to the top-level object and are matched exactly in
the original payload, without Unicode normalization. Arrays and scalars are
valid JSON when no keys are required. JSON validity and required keys form one
combined check. Each enabled lexical category also forms one check, regardless
of how many terms it contains. A report with zero enabled checks scores 1.0.

## Reviewed Python fixture execution

Create `a.py`:

```python
def solve(values: list[int]) -> int:
    return sum(values)
```

Create `b.py`:

```python
def solve(values: list[int]) -> int:
    return values[0]
```

Create `fixtures.py`:

```python
assert solve([2, 3]) == 5
assert solve([]) == 0
```

```bash
vi-en-grade grade-ab --model-a a.py --model-b b.py --tests fixtures.py --function solve --timeout 2.5
```

Both sources pass through the AST gate before execution. Imports default to a
small standard-library allowlist. Restricted builtin references are rejected
before aliasing; private attribute access, wildcard imports, and relative imports
are rejected. Syntax errors and a missing required top-level function block
execution. Missing annotations, syntactically mutable defaults, and bare
`except` clauses are diagnostics that do not block runtime checks.

The branch complexity estimate is one plus decisions across the whole module:
conditionals, conditional expressions, loops, exception handlers, Boolean
operators, comprehension generators and filters, and non-default match cases
and guards. It excludes `with` and `assert`. It is a transparent syntactic
estimate, not per-function control-flow analysis, and does not rank candidates.
Annotation presence does not establish type correctness. Mutable defaults are
recognized for literals, comprehensions, common builtin constructors, and tuples
containing them; aliases and arbitrary factories are not resolved.

The child runs with `-I -B -X utf8`, no inherited environment except Windows
`SYSTEMROOT` when present, no interactive input, and a temporary working directory.
Candidate and fixture code compile separately, preserving future imports. The
wrapper catches actual exception types: assertion failures, other exceptions
(including `SystemExit`), and timeouts have distinct statuses. Each output stream
retains at most 4,000 bytes while excess output is drained; `output_truncated`
indicates truncation. A timeout diagnostic can extend the returned stderr text.
Invalid UTF-8 output is replaced during decoding. Durations include process and
temporary-file overhead and are not benchmarks.

Runtime pass means that the fixture program completed without an exception.
Fixtures must contain meaningful assertions. Candidate globals are visible to
fixtures; this is not a tamper-resistant evaluation protocol. The AST gate cannot
prove Python code safe, and the subprocess has no OS filesystem, network, memory,
or descendant-process isolation. See [the security boundary](../SECURITY.md).
The [Python interpreter documentation](https://docs.python.org/3.13/using/cmdline.html#cmdoption-I)
describes isolated import behavior, which is distinct from OS sandboxing.

Ranking first compares runtime pass/fail. When both pass, fewer static diagnostics
wins; equal counts yield `tie_both_pass`, even when both have diagnostics. When
neither passes, the result is `tie_both_fail`. A rationale reports fixture outcomes
and issue counts; it does not infer overall model quality from one case.

## Agreement inputs and definitions

For Cohen's kappa, save `ratings.json`:

```json
{
  "rater_a_labels": ["model_a", "model_b", "tie"],
  "rater_b_labels": ["model_a", "tie", "tie"],
  "production_threshold": 0.65
}
```

Sequences must be nonempty and aligned by item before calling this API. For
existing linked datasets, use `vi-en-compare` to align by response-pair ID.
Standalone arrays do not perform ID alignment.

For Fleiss' kappa, save `multi_ratings.json`:

```json
{
  "ratings_matrix": [["A", "A", "B"], ["B", "B", "B"], ["A", "A", "A"]],
  "production_threshold": 0.60
}
```

Rows are items; entries are nominal categorical labels from raters. Every row
must contain the same number of ratings, at least two. Missing ratings and
unequal row sizes are rejected. Both metrics use `(observed - expected) /
(1 - expected)`. Cohen uses the two marginal distributions; Fleiss uses pooled
category proportions and within-item pair agreement. Fleiss' chance model follows
the fixed-number-of-ratings definition documented by
[statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.stats.inter_rater.fleiss_kappa.html).

Integer counts determine the numerator and denominator before division. If
expected agreement is exactly one, kappa is `null` with
`undefined_reason: "expected_agreement_is_one"`; it is not assigned 1.0.
Threshold comparisons use the unrounded coefficient. Thresholds must be finite
and within [-1, 1]. The `passes_production_threshold` field is only a configurable
numeric comparison, not evidence of deployment readiness or statistical
significance. No confidence intervals or significance tests are calculated.

Cohen's descriptive interpretation bands are `poor` below 0, `slight` on [0, .2),
`fair` on [.2, .4), `moderate` on [.4, .6), `substantial` on [.6, .8), and
`almost_perfect` on [.8, 1]. Undefined coefficients have no interpretation band.
These coarse labels do not replace consideration of prevalence and sample size.

For position swaps, save `swaps.json`:

```json
{
  "pairs": [
    {"item_id": "case-1", "forward_verdict": "model_a", "swapped_verdict": "model_b"},
    {"item_id": "case-2", "forward_verdict": "model_a", "swapped_verdict": "model_a"}
  ]
}
```

Labels denote displayed positions in each ordering: `model_a` is always the first
position, including after the candidates swap. A/B and B/A preserve the winning
candidate, and tie/tie is consistent. Other combinations are inconsistent.
`first_position_bias_rate` counts A/A pairs divided by all pairs, including ties;
it is not the fraction of individual first-position selections. Item IDs must
be unique and nonblank. Inconsistency can have causes other than position bias.

## Combined reports and Python APIs

```bash
vi-en-grade grade-ab --model-a a.py --model-b b.py --tests fixtures.py --function solve --constraints constraints.json --ratings ratings.json
```

Optional constraints apply to both source texts; optional ratings add Cohen's
kappa. All files are read and optional JSON inputs are validated before either candidate launches. Individual
`ifeval`, `kappa`, `fleiss`, and `swap-bias` commands never execute source code.

```python
from vi_en_eval.verifiers import IFEvalConstraintSpec, verify_instruction_following
from vi_en_eval.calibration import compute_cohens_kappa

report = verify_instruction_following("Đà Nẵng", IFEvalConstraintSpec(min_words=2))
agreement = compute_cohens_kappa(["A", "B"], ["A", "B"])
assert report.passed and agreement.kappa == 1.0
```

Successful input produces `{"schema_version": 1, "report": ...}`. Input errors
produce `{"schema_version": 1, "error": {"code": ..., "message": ...}}` without a
traceback. Exit status is 0 for a successful evaluation, 1 for input errors,
failed IFEval constraints, or two failing code candidates, and 2 for command-line
usage errors. In a combined run, both instruction checks must pass and at least
one code candidate must pass. Calibration threshold results do not change the
exit status. JSON keys are sorted; runtime durations and temporary paths may vary.

Tests cover Vietnamese NFC/NFD, strict JSON decoding, Markdown subset boundaries,
restricted aliases, all function argument kinds, mutable-default counterexamples,
exception classification, bounded output, timeouts, exact agreement fractions,
degenerate marginals, and all nine swap verdict combinations. Existing dataset
validation tests remain independent of source execution.
