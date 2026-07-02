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

- **Syntax error:** The `if value > 0` line is missing a colon.
- **Logic error:** The denominator uses `len(numbers)` instead of
  `len(positives)`.
- **Missing edge case:** The function divides by zero when the input has no
  positive numbers.
- **Incomplete explanation:** The explanation does not mention the required
  `0.0` fallback.

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
| Instruction following | 2 | Attempts the requested function but misses the fallback behavior. |
| Correctness | 1 | Syntax error and incorrect denominator make the answer unreliable. |
| Completeness | 2 | Does not handle empty positive set. |
| Clarity | 3 | Intent is visible, but explanation omits critical behavior. |
| Edge-case handling | 1 | Fails the no-positive-number case. |
| Safety/reliability | 2 | Could raise `SyntaxError` or `ZeroDivisionError`. |

## Reviewer Rationale

This answer should be rated weak because it cannot run as written and does not
meet the main behavioral requirement. The most important fixes are adding the
missing colon, dividing by the number of positive values, and returning `0.0`
when no positive values exist.

## Edge Cases

- `average_positive([1, 2, 3])` should return `2.0`.
- `average_positive([-2, 0, -5])` should return `0.0`.
- `average_positive([10, -5, 0, 20])` should return `15.0`.
- `average_positive([])` should return `0.0`.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client code, paid task content, real model
outputs, screenshots, or project codenames.
