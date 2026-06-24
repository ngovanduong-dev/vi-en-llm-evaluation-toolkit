# Vietnamese-English Response Comparison

## Task Type

Bilingual response comparison and evaluator rationale writing.

## User Prompt

A Vietnamese student asks for an English email requesting a two-day extension
from a professor. The response should be polite, specific, and should not
invent personal excuses.

## Response A

Dear Professor Nguyen,

I hope you are doing well. I am writing to respectfully ask whether it would be
possible to extend the deadline for my history assignment by two days. I
understand the importance of submitting work on time and appreciate your
consideration.

Sincerely,
Minh

## Response B

Hey teacher,

I cannot finish because my family had a serious emergency. Can I send it
sometime next week? Thanks.

## Evaluation Criteria

- Preserve a respectful academic tone.
- Mention the requested two-day extension clearly.
- Avoid inventing a personal excuse.
- Use natural English suitable for a professor.
- Keep the message concise and complete.

## Rubric Scores

| Criterion | Response A | Response B |
| --- | ---: | ---: |
| Instruction following | 5 | 2 |
| Correctness | 5 | 2 |
| Completeness | 4 | 2 |
| Clarity | 5 | 3 |
| Language naturalness | 5 | 3 |
| Formatting | 5 | 3 |
| Safety | 5 | 3 |

## Winner

Response A

## Reviewer Rationale

Response A wins because it preserves the requested formal tone, states the
two-day extension clearly, and avoids adding unsupported personal details.
Response B is understandable, but it is too casual for a professor, changes the
requested timeline to "sometime next week," and invents a family emergency that
the user did not provide.

## Key Issues Found

- **Tone mismatch, high severity:** Response B uses "Hey teacher," which is too
  informal for the academic context.
- **Missing constraint, medium severity:** Response B does not preserve the
  two-day extension request.
- **Unsupported detail, high severity:** Response B invents a family emergency,
  creating a hallucination-style issue.

## Better Response Direction

A stronger response should keep the message polite, name the exact extension
requested, and avoid adding a reason unless the user supplies one.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client data, paid task content, real model
outputs, screenshots, or project codenames.
