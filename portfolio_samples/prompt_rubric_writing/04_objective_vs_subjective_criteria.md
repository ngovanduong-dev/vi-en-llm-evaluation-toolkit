# Objective vs Subjective Criteria

## Synthetic Prompt

Evaluate an English answer that explains the difference between JSON and JSONL
to a beginner. The answer should be accurate, concise, include one valid JSONL
example with two lines, and warn that blank lines are usually invalid in strict
JSONL datasets.

## Prompt Design Goal

This sample shows how to separate mechanically checkable requirements from
quality judgments that require reviewer interpretation.

## Constraints Included

- Topic: JSON vs JSONL.
- Audience: beginner.
- Include a valid JSONL example.
- Example must contain two lines.
- Mention blank-line risk in strict JSONL datasets.
- Keep the answer concise.

## Explicit Requirements

- Explain the difference between JSON and JSONL.
- Include one JSONL example with two lines.
- Warn about blank lines in strict JSONL datasets.
- Keep the answer concise.

## Implicit Requirements

- Avoid assuming the beginner knows records, arrays, or parsers.
- Use technically accurate but simple wording.
- Avoid overclaiming that all tools enforce the same JSONL rules.
- Make the example easy to copy and inspect.

## Rubric Criteria

| Criterion | Objective or subjective | Strong performance |
| --- | --- | --- |
| JSON vs JSONL distinction | Objective | Explains that JSON is one JSON value while JSONL stores one JSON object/value per line. |
| Valid two-line JSONL example | Objective | Provides exactly two non-empty lines, each independently valid JSON. |
| Blank-line warning | Objective | States that blank lines can make strict JSONL validation fail. |
| Beginner clarity | Subjective | Uses simple wording without unnecessary parser jargon. |
| Concision | Subjective | Covers the required points without long tangents. |
| Technical nuance | Subjective | Avoids absolute claims about every tool while still giving practical guidance. |

## Objective Criteria

- The response includes exactly two JSONL example lines.
- Each JSONL line can be parsed as JSON.
- The response says JSONL is line-oriented.
- The response warns about blank lines.

## Subjective Criteria

- The explanation is beginner-friendly.
- The answer is concise enough for a quick learning context.
- The nuance about tools and validation is accurate without overwhelming the
  user.

## Common Failure Modes

- Showing a JSON array instead of JSONL.
- Including a trailing comma in the JSONL example.
- Using three or more example lines despite the prompt asking for two.
- Saying blank lines are always accepted.
- Being technically correct but too dense for a beginner.

## Why This Is Portfolio-Safe

This sample uses public technical concepts and original wording. It does not
contain private code, client schemas, platform guidelines, paid task prompts, or
real model outputs.
