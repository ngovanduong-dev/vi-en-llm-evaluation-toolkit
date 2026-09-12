# Python Code Review

## User Prompt

Write a Python function `average_positive(numbers)` that returns the average of
positive numbers in a list. If there are no positive numbers, return `0.0`.

## AI Technical Response

```python
def average_positive(numbers):
    positives = []
    for value in numbers:
        if value > 0
            positives.append(value)
    return sum(positives) / len(numbers)
```

The code loops through the list and averages the positive values.

## Technical Issues Found

- **Syntax error:** The missing colon after `if value > 0` causes `SyntaxError`;
  the original code cannot execute normally.
- **Logic error after a colon-only repair:** The denominator is `len(numbers)`,
  so mixed positive/non-positive input is not averaged over positive values only.
- **Empty-input failure after a colon-only repair:** `[]` raises
  `ZeroDivisionError`. A nonempty all-nonpositive list such as `[-2, 0, -5]`
  returns `0.0`; it does not divide by zero.
- **Incomplete explanation:** The explanation does not mention the required
  behavior of returning `0.0` when no positive values exist.

## Controlled Reproduction

The reviewed synthetic snippet was checked as written, then a scratch copy was
run after adding only the missing colon (Python 3.13.9). The original produces
`SyntaxError: expected ':'` at line 4, column 21, before any function call.

| Input | Colon-only result | Required result |
| --- | --- | --- |
| `[]` | `ZeroDivisionError: division by zero` | `0.0` |
| `[-2, 0, -5]` | `0.0` | `0.0` |
| `[10, -5, 0, 20]` | `7.5` | `15.0` |
| `[1, 2, 3]` | `2.0` | `2.0` |

For the mixed input, the positive sum is 30 but the code divides by four input
elements rather than two positive elements. For the nonempty all-nonpositive
input, the calculation is `0 / 3`; for empty input, the denominator is zero.
The required behavior does not prescribe an explicit conditional branch.

## Corrected Direction

```python
def average_positive(numbers):
    positives = [value for value in numbers if value > 0]
    if not positives:
        return 0.0
    return sum(positives) / len(positives)
```

The corrected version parses valid Python, averages only positive values, and
handles the no-positive-number case explicitly.

## Rubric Scores

| Criterion | Score | Reviewer note |
| --- | ---: | --- |
| Instruction following | 2 | Cannot run as written; the colon-only repair still fails required behavior. |
| Correctness | 1 | Syntax error and incorrect denominator make the answer unreliable. |
| Completeness | 2 | After the colon-only repair, empty input is still unhandled. |
| Clarity | 3 | Intent is visible, but explanation omits critical behavior. |
| Edge-case handling | 1 | After the colon-only repair, empty input raises instead of returning 0.0. |
| Safety/reliability | 2 | Original code fails with `SyntaxError`; the colon-only repair raises `ZeroDivisionError` on empty input. |

## Reviewer Rationale

This answer should be rated weak because it cannot run as written and does not
meet the main behavioral requirement. The most important fixes are adding the
missing colon, dividing by the number of positive values, and returning `0.0`
when no positive values exist, including empty input. These are behavioral
requirements; the conditional in the corrected direction is one implementation.
The scores above assess the original response, with latent defects identified
through the controlled repair. They use the historical sample-specific criteria,
not the seven-field `TechnicalRubricScores` model.

## Edge Cases

- `average_positive([1, 2, 3])` should return `2.0`.
- `average_positive([-2, 0, -5])` should return `0.0`.
- `average_positive([10, -5, 0, 20])` should return `15.0`.
- `average_positive([])` should return `0.0`.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client code, paid task content, real model
outputs, screenshots, or project codenames.
