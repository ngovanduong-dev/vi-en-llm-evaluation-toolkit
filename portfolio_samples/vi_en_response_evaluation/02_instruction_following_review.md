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
- Keep the message under 60 words.
- Use a professional and empathetic customer-service tone.
- Include an apology.
- Avoid blaming the customer.
- Explain the delay without adding unsupported specifics.

## Rubric Scores

| Criterion | Response A | Response B |
| --- | ---: | ---: |
| Instruction following | 5 | 2 |
| Correctness | 5 | 3 |
| Completeness | 4 | 2 |
| Clarity | 5 | 4 |
| Language naturalness | 5 | 3 |
| Formatting | 5 | 4 |
| Safety | 5 | 3 |

## Winner

Response A

## Reviewer Rationale

Response A follows the core constraints: it is concise, apologetic,
professional, and does not blame the customer. Response B is still in
Vietnamese and mostly understandable, but it weakens instruction following by
suggesting the customer's address may be the problem and by adding a specific
shipping-carrier explanation that the prompt did not provide.

## Key Issues Found

- **Customer-blaming risk, high severity:** Response B says the address may be
  unclear, which conflicts with the "không đổ lỗi cho khách" requirement.
- **Unsupported cause, medium severity:** Response B introduces carrier
  overload without evidence from the prompt.
- **Tone issue, medium severity:** "Bạn vui lòng chờ thêm" sounds less
  empathetic than a customer-service apology.

## Better Response Direction

The better answer should acknowledge the delay, apologize directly, explain
that the team is checking the order, and avoid assigning fault.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client data, paid task content, real model
outputs, screenshots, or project codenames.
