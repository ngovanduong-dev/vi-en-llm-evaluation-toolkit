# Coding Response Review Rubric

Use this rubric for AI-generated coding explanations or code snippets.

## Review Categories

- Syntax error
- Logic error
- Missing edge case
- Runtime risk
- API misuse
- Unsupported library or function claim
- Inefficient solution
- Missing explanation
- Invalid JSON or malformed structured output

## Scoring Notes

- A strong answer should satisfy the prompt, explain assumptions, and avoid
  unsupported claims about APIs or libraries.
- A weak answer may look plausible while omitting edge cases, returning invalid
  JSON, or relying on functions that do not exist.
- When possible, evaluator notes should name the exact error type and suggest a
  concrete fix.

## Technical Model Dimensions

`TechnicalRubricScores` in `src/vi_en_eval/technical_models.py` contains all seven
fields below. Scores 2 and 4 fall between the neighboring anchors and require
an evidence-based explanation.

| Dimension / field | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Instruction following / `instruction_following` | Misses core task requirements | Meets some requirements with material gaps | Meets all important supplied constraints |
| Correctness / `correctness` | Core logic or claims are wrong | Main approach is sound but has limited errors | Behavior and claims match the available requirements and evidence |
| Edge-case handling / `edge_case_handling` | Fails a required boundary case | Handles ordinary cases but misses a relevant boundary | Handles relevant boundary and failure cases |
| Efficiency / `efficiency` | Resource use makes the approach unsuitable for the stated workload | Workable with avoidable resource costs | Resource use is appropriate for the stated workload and constraints |
| Maintainability / `maintainability` | Structure makes safe understanding or changes difficult | Understandable but unnecessarily difficult to change | Clear structure and appropriate simplicity support changes |
| Security/reliability / `security_reliability` | Introduces a serious security or operational failure | Has a limited, concrete security or reliability weakness | No identified security/reliability defect under the stated assumptions |
| Explanation quality / `explanation_quality` | Explanation is absent when needed or materially misleading | Explains the main approach but leaves relevant gaps | Accurately explains behavior, assumptions, and relevant limitations |

Apply dimensions to the actual task. Do not invent scale requirements, demand
an optimization without a workload, or penalize missing code when the prompt
asks for an explanation. Missing evidence and inapplicability are not proof of
excellence. The model requires seven numeric scores and has no N/A field; state
such limits in the candidate rationale so required numbers do not conceal them.
Historical single-response Markdown reviews use their own six named criteria;
they are not serialized `TechnicalRubricScores` records and cannot be converted
by renaming completeness or clarity to an unrelated technical dimension.

## Findings and Pairwise Judgments

The checklist above uses human-readable review labels. The model's eight issue
categories are `Correctness/Logic`, `Edge Case`, `Efficiency`, `API/Contract`,
`Security/Reliability`, `Concurrency`, `Explanation`, and `Structured Output`.
Choose a category for the evidenced defect; categories are not score dimensions.

Use Low for a minor localized defect, Medium for a material but limited effect,
and High for a core requirement failure or serious operational/security impact.
Severity measures the stated consequence, not a fixed numeric deduction.
A crash may affect correctness and reliability for distinct reasons; explain
both. Tone alone is not a security/reliability defect.

`PairwiseTechnicalEvaluation` stores separate `candidate_a` and `candidate_b`
scores, findings, and rationales, plus an overall A/B/Tie winner, numeric
confidence from 0 to 1, and comparison rationale. Confidence is an evaluator's
assessment, not a calibrated probability. Choose the overall preference from
requirements and evidence; the model does not calculate it from scores.

Distinguish original code from controlled repairs. A syntax failure prevents
normal execution; a runtime defect observed after a repair must be labeled as
conditional on that repair. Parsing, individual-record validation, and dataset
integrity checks do not establish evaluator correctness. Do not execute
arbitrary response text; any reproduction must use a reviewed synthetic fixture.
