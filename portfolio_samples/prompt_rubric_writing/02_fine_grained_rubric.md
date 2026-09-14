# Fine-Grained Rubric

## Synthetic Prompt

Compare two Vietnamese answers to a user asking how to explain a delayed
delivery to a customer. The better answer should be empathetic, professional,
specific enough to be useful, and should avoid blaming the customer.

## Prompt Design Goal

This sample shows how to convert a broad quality target into atomic rubric
criteria that a reviewer can apply consistently.

## Constraints Included

- Evaluate two responses, not just one.
- Focus on Vietnamese customer-service quality.
- Consider empathy, professionalism, specificity, and blame avoidance.
- Explain the comparison; use a preference only where supported.

## Explicit Requirements

- Compare two responses.
- Judge customer-service tone.
- Prefer an answer that does not blame the customer.
- Compare against empathy, professionalism, specificity, and blame avoidance.

## Implicit Requirements

- A stronger answer should preserve user trust.
- A stronger answer should avoid unsupported details about logistics.
- The rationale should cite concrete text-level differences, not personal taste.

## Rubric Criteria

| Criterion | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Empathy | No apology or empathy | Some polite wording but limited empathy | Clear apology and customer-centered wording |
| Professional tone | Casual, defensive, or blaming | Mostly professional with uneven phrasing | Professional and suitable for customer support |
| Constraint adherence | Misses major prompt constraints | Follows some constraints | Follows all important constraints |
| Specificity | Too vague to be useful | Gives a basic next step | Gives a clear, realistic next step without inventing details |
| Localization quality | Unnatural or over-literal Vietnamese | Understandable but awkward | Natural Vietnamese for customer-service context |
| Rationale quality | Generic preference statement | Mentions one or two differences | Explains concrete strengths, weaknesses, and winner logic |

## Objective Criteria

- The review addresses both candidate responses.
- The review identifies whether customer blame is present.
- Any factual delay cause asserted by a candidate is checked against supplied
  evidence; the scenario alone supplies no cause.

The empathy, tone, constraint, specificity, and localization rows assess the
customer-service candidates. Rationale quality assesses the evaluator's review.
These are distinct targets, not one score set. A winner label and discussion of
strengths and weaknesses can help explain a comparison, but the source does not
explicitly require either. Do not invent a weakness or force a winner when the
evidence supports a Tie. No candidate pair is supplied in this rubric exercise.

## Subjective Criteria

- Whether the tone feels empathetic enough for a real customer-support message.
- Whether the next step is specific without sounding overpromising.
- Whether Vietnamese phrasing feels natural rather than translated.

## Common Failure Modes

- Using one broad score such as "good" without criterion-level evidence.
- Rewarding a longer answer even when it invents details.
- Ignoring tone because the answer is factually understandable.
- Treating natural Vietnamese style as purely subjective and not explaining why.

## Why This Is Portfolio-Safe

The prompt, rubric, and examples are synthetic. They are not copied from a
platform guideline, paid task, client rubric, or real evaluation queue.
