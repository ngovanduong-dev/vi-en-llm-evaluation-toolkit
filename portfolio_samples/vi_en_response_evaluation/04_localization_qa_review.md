# Vietnamese Localization QA Review

## Task Type

Vietnamese localization and tone review.

## User Prompt

Localize this English app message into natural Vietnamese for a mobile banking
app. Keep it professional, clear, and reassuring.

```text
Your transfer is being reviewed. We will notify you when it is complete.
```

## Response A

Giao dịch chuyển tiền của quý khách đang được xem xét. Chúng tôi sẽ thông báo
khi giao dịch hoàn tất.

## Response B

Sự chuyển khoản của bạn đang bị đánh giá. Chúng tôi sẽ báo bạn khi nó xong.

## Evaluation Criteria

- Use natural Vietnamese for a banking app.
- Preserve the meaning of "being reviewed" without sounding alarming.
- Keep a professional and reassuring tone.
- Avoid over-literal English-to-Vietnamese phrasing.
- Make the message clear to a general mobile-app user.

## Rubric Scores

| Criterion | Response A | Response B |
| --- | ---: | ---: |
| Instruction following | 5 | 2 |
| Correctness | 5 | 3 |
| Completeness | 5 | 3 |
| Clarity | 5 | 3 |
| Language naturalness | 5 | 1 |
| Formatting | 5 | 4 |
| Safety | 5 | 3 |

## Winner

Response A

## Reviewer Rationale

Response A is appropriate for a Vietnamese mobile banking context: "giao dịch
chuyển tiền" and "đang được xem xét" are clear, professional, and not overly
alarming. Response B is an over-literal translation. "Sự chuyển khoản" is
unnatural, "đang bị đánh giá" sounds negative or punitive, and "khi nó xong" is
too casual for financial messaging.

## Key Issues Found

- **Unnatural localization, high severity:** "Sự chuyển khoản" is not natural
  product Vietnamese.
- **Tone risk, medium severity:** "Đang bị đánh giá" can imply blame or a
  negative judgment.
- **Register mismatch, medium severity:** "Báo bạn khi nó xong" is too casual
  for a banking notification.

## Better Response Direction

Use familiar Vietnamese banking terminology, keep the tone neutral and
reassuring, and avoid translating English structure word-for-word.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client data, paid task content, real model
outputs, screenshots, or project codenames.
