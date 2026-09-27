# Technical Python Case Evidence

This directory contains three linked, synthetic technical-evaluation cases:

- `prompts.jsonl` defines explicit source requirements.
- `response_pairs.jsonl` stores two plausible candidate answers per prompt.
- `technical_evaluations.jsonl` stores candidate-specific scores, findings,
  rationales, winners, and evaluator confidence.

The records are public-safe examples, not a representative benchmark or
independent expert adjudication. Confidence is stored evaluator judgment, not a
calibrated probability. Structural validation cannot prove that a technical
judgment is semantically correct.

## Evidence Boundary

Candidate response strings are data and are never executed. The executable
evidence uses manually reviewed fixture implementations in
[`tests/fixtures/technical_case_implementations.py`](../../tests/fixtures/technical_case_implementations.py).
Those fixtures encode only the behavior needed for these synthetic cases.
[`tests/test_technical_case_evidence.py`](../../tests/test_technical_case_evidence.py)
separately checks record structure, linked-dataset integrity, discriminating
behavior, and agreement between observed evidence and stored rationales.

Reproduce the evidence from the repository root:

```bash
python -m pytest tests/test_technical_case_evidence.py --no-cov
```

Validate the linked files through the installed workflow:

```bash
vi-en-dataset \
  --prompts data/technical_python/prompts.jsonl \
  --responses data/technical_python/response_pairs.jsonl \
  --evaluations data/technical_python/technical_evaluations.jsonl
```

## Case Map

| Case | Decisive requirement | Minimal oracle | Observed distinction |
| --- | --- | --- | --- |
| `python_iterable_mean_001` | Accept a one-shot iterable and count only positive values | `iter([2.0, -1.0, 4.0])` must produce `3.0` | A consumes the iterator while counting and returns `0.0`; B returns `3.0` |
| `python_call_isolation_002` | Every call must contain only that call's words | Call once with `['ant']`, then with `['bear']`; the second result must be `{'b': ['bear']}` | A returns independent mappings; B's mutable default retains the `a` group |
| `python_stable_dedup_003` | Accept unhashable equality-comparable values and preserve first occurrences | `[['x'], ['y'], ['x']]` must become `[['x'], ['y']]` | A raises `TypeError`; B returns the required list |

## Complexity Assumptions

The iterable-mean solution needs one input pass, O(n) time, and O(1)
additional memory. Candidate A also uses constant additional memory, but its
second pass is invalid for a one-shot iterable; ordinary list input hides that
defect. Empty, all-nonpositive, mixed, one-shot, and positive-denominator cases
are covered.

Both grouping implementations perform O(n) expected dictionary operations and
use O(n) result memory under normal hashing assumptions. The decisive failure is
not asymptotic: Candidate B reuses one dictionary across calls, contrary to the
explicit independence contract.

For stable deduplication, Candidate A's dictionary construction is O(n) average
time for hashable values under normal hashing assumptions and can degrade with
pathological collisions. It is invalid for the declared unhashable domain.
Candidate B uses O(n) result memory and O(n^2) equality comparisons in the worst
case. Its response states that trade-off; neither case claims unconditional
worst-case O(1) set or dictionary membership.
