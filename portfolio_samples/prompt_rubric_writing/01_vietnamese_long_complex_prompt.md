# Vietnamese Long Complex Prompt

## Synthetic Prompt

Bạn là trợ lý viết nội dung cho một trung tâm học tiếng Anh online. Hãy viết
một email tiếng Việt gửi phụ huynh về việc lớp học tối thứ Sáu phải đổi sang
tối thứ Bảy tuần này.

Yêu cầu:

- Giữ giọng lịch sự, chuyên nghiệp, không đổ lỗi cho giáo viên hoặc phụ huynh.
- Nêu rõ lịch mới là 19:30-21:00, thứ Bảy ngày 18/07.
- Giải thích ngắn gọn rằng thay đổi nhằm đảm bảo chất lượng buổi học.
- Có lời xin lỗi vì sự bất tiện.
- Kết thúc bằng lời mời phụ huynh phản hồi nếu lịch mới không phù hợp.
- Không quá 160 từ.
- Không dùng biểu tượng cảm xúc.

## Prompt Design Goal

This prompt tests whether a response can follow multiple Vietnamese business
communication constraints at the same time: tone, date/time accuracy,
word-limit control, no unsupported blame, and a clear call to action.

## Constraints Included

- Audience: parents of online English students.
- Language: Vietnamese.
- Format: email-style announcement.
- Tone: polite and professional.
- Required details: new class time and date.
- Safety/context guardrail: do not blame teachers or parents.
- Length limit: under 160 words.

## Explicit Requirements

- Write in Vietnamese.
- Mention the new schedule: 19:30-21:00, Saturday 18/07.
- Apologize for inconvenience.
- Explain that the change supports class quality.
- Invite parents to respond if the new schedule is not suitable.
- Avoid emojis.
- Stay under 160 words.

## Implicit Requirements

- The response should be easy for busy parents to scan.
- The reason should sound neutral and reassuring.
- The email should not create anxiety about class reliability.
- The message should preserve the relationship between the center and parents.

## Rubric Criteria

| Criterion | Strong performance |
| --- | --- |
| Language match | The full response is written in natural Vietnamese. |
| Schedule accuracy | The response states both the correct time and date without changing them. |
| Tone control | The response sounds polite, professional, and parent-facing. |
| Constraint coverage | The response includes apology, reason, and response invitation. |
| No unsupported blame | The response does not blame teachers, parents, or students. |
| Length control | The response stays under 160 words. |

## Objective Criteria

- The response is in Vietnamese.
- The schedule is exactly 19:30-21:00, thứ Bảy ngày 18/07.
- The response is 160 words or fewer.
- No emoji appears.
- A parent response invitation is present.

## Subjective Criteria

- The tone is appropriately professional.
- The explanation feels reassuring rather than vague or defensive.
- The wording sounds natural for Vietnamese parent communication.

## Common Failure Modes

- Changing the date, time, or weekday.
- Adding an unsupported reason such as teacher illness.
- Writing too casually for parents.
- Omitting the apology or response invitation.
- Producing a message that is technically correct but too stiff or unnatural.

## Why This Is Portfolio-Safe

This prompt is fully synthetic and generalized. It is designed to demonstrate
Vietnamese prompt design and rubric reasoning without exposing private platform
tasks, internal guidelines, client data, real model outputs, screenshots, or
paid task content.
