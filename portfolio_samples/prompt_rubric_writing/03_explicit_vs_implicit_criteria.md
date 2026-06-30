# Explicit vs Implicit Criteria

## Synthetic Prompt

Viết một phản hồi tiếng Việt cho người dùng hỏi cách từ chối lời mời làm thêm
cuối tuần. Câu trả lời phải lịch sự, không quá dài, có một câu mẫu để người
dùng có thể gửi ngay, và không khuyên người dùng nói dối.

## Prompt Design Goal

This sample separates requirements directly stated in the prompt from reasonable
quality expectations that are implied by the task.

## Constraints Included

- Vietnamese answer.
- Polite refusal advice.
- Concise length.
- Include a ready-to-send sample sentence.
- Do not encourage lying.

## Explicit Requirements

- The answer must be in Vietnamese.
- The answer must be polite.
- The answer must not be too long.
- The answer must include a ready-to-send sentence.
- The answer must not advise the user to lie.

## Implicit Requirements

- The sample sentence should preserve the relationship with the inviter.
- The answer should not pressure the user to over-explain.
- The advice should respect the user's boundary.
- The response should be practical, not only abstract.

## Rubric Criteria

| Criterion | Strong performance |
| --- | --- |
| Explicit language compliance | The response is written in Vietnamese. |
| Politeness | The refusal is respectful and avoids harsh wording. |
| Practicality | The response includes a concrete sentence the user can send. |
| Ethical advice | The response does not recommend fake reasons or dishonest excuses. |
| Boundary support | The advice lets the user decline without over-explaining. |
| Concision | The answer is brief enough for the user's request. |

## Objective Criteria

- Vietnamese is used.
- A send-ready sentence is included.
- No instruction to lie appears.
- The response gives refusal wording rather than only general advice.

## Subjective Criteria

- The refusal sounds warm enough for Vietnamese social context.
- The explanation is concise but not abrupt.
- The sample sentence balances honesty and politeness.

## Common Failure Modes

- Giving only general tips and no sample sentence.
- Suggesting a false reason to make refusal easier.
- Writing a message that is polite but too long for quick use.
- Treating "không quá dài" as vague and ignoring length control.
- Creating an overly formal tone for a casual invitation.

## Why This Is Portfolio-Safe

This sample uses a generalized everyday scenario. It does not include private
task data, internal guidelines, real model outputs, client materials, or paid
platform content.
