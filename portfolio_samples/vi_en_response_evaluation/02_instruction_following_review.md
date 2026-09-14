# Instruction-Following Review

## Task Type

Vietnamese instruction-following evaluation.

## User Prompt

Viết bằng tiếng Việt một tin nhắn ngắn cho khách hàng về việc đơn hàng giao
chậm. Yêu cầu: giọng chuyên nghiệp, không đổ lỗi cho khách, có lời xin lỗi, và
không quá 60 từ.

## Response A

Chúng tôi xin lỗi vì đơn hàng của quý khách giao chậm hơn dự kiến. Đội ngũ
đang kiểm tra và sẽ cập nhật thời gian giao hàng sớm nhất. Cảm ơn quý khách đã
thông cảm.

## Response B

Đơn hàng của bạn bị chậm vì bên vận chuyển đang quá tải và cũng có thể do địa
chỉ nhận hàng chưa rõ. Bạn vui lòng chờ thêm, chúng tôi sẽ cố gắng xử lý khi có
thể.

## Evaluation Criteria

- Answer in Vietnamese.
- Keep the message at most 60 words.
- Use a professional and empathetic customer-service tone.
- Include an apology.
- Avoid blaming the customer.
- Explain the delay without adding unsupported specifics.

## Rubric Scores

| Criterion | Response A | Response B |
| --- | ---: | ---: |
| Instruction following | 5 | 2 |
| Correctness | 4 | 3 |
| Completeness | 5 | 3 |
| Clarity | 5 | 4 |
| Language naturalness | 5 | 4 |
| Formatting | 5 | 5 |
| Safety | 5 | 5 |

## Winner

Response A

## Reviewer Rationale

Response A follows the core constraints: it is concise, apologetic,
professional, and does not blame the customer. Response B is still in
Vietnamese and mostly understandable, but it weakens instruction following by
suggesting the customer's address may be the problem and by adding a specific
shipping-carrier explanation that the prompt did not provide.

A also asserts that the team is already checking the order and will provide an
update soon. The prompt supplies neither fact. These are plausible service
assurances, but they need confirmation before being sent; correctness is 4,
not 5. They do not outweigh B's missing apology, blame, and invented cause.

Both responses meet the inclusive 60-word limit (37 and 39 whitespace-separated
units respectively; this is a counting convention, not Vietnamese lexical word
segmentation). A covers all requested components (completeness 5); B omits the
apology (completeness 3). B's "khi có thể" is vague (clarity 4), while its
Vietnamese is grammatical but less suited to empathetic service communication
(language naturalness 4). Both paragraphs have suitable structure (formatting
5). No concrete safety violation is established by the blame or tone defects
(safety 5). Instruction following separately reflects the explicit apology,
professional-tone, and no-blame requirements.

## Key Issues Found

- **Customer-blaming risk, high severity:** Response B says the address may be
  unclear, which conflicts with the "không đổ lỗi cho khách" requirement.
- **Unsupported cause, medium severity:** Response B introduces carrier
  overload without evidence from the prompt.
- **Missing apology, high severity:** B gives no apology despite the explicit requirement.
- **Unverified assurance, low severity:** A states an ongoing check and near-term
  update without source support. Confirm those details or phrase them as a
  proposed next step.
- **Tone issue, medium severity:** "Bạn vui lòng chờ thêm" sounds less
  empathetic than a customer-service apology.

## Better Response Direction

The better answer should acknowledge the delay, apologize directly, avoid
assigning fault, and include only verified operational details. A next step may
be proposed without claiming it is already underway.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client data, paid task content, real model
outputs, screenshots, or project codenames.
