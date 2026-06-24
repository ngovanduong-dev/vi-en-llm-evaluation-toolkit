# Hallucination Detection Review

## Task Type

Bilingual hallucination and factual-plausibility review.

## User Prompt

Summarize the Vietnamese product update below in English. Do not add dates,
prices, statistics, or features that are not present.

```text
Ứng dụng ghi chú LumenNote vừa bổ sung chế độ làm việc ngoại tuyến và tùy chọn
đồng bộ thủ công. Nhóm phát triển cho biết họ sẽ tiếp tục cải thiện tốc độ mở
tệp trong các bản cập nhật sau.
```

## Response A

LumenNote has added offline mode and a manual sync option. The development team
also said it will keep improving file-opening speed in future updates.

## Response B

LumenNote launched a major 2026 update with offline mode, manual sync, faster
file opening, and a new $4.99 monthly premium plan. The company said these
features are already available worldwide.

## Evaluation Criteria

- Preserve only facts present in the Vietnamese source.
- Translate the meaning into natural English.
- Avoid invented dates, prices, release scope, or feature status.
- Distinguish current features from planned improvements.
- Keep the summary concise.

## Rubric Scores

| Criterion | Response A | Response B |
| --- | ---: | ---: |
| Instruction following | 5 | 1 |
| Correctness | 5 | 1 |
| Completeness | 5 | 3 |
| Clarity | 5 | 4 |
| Language naturalness | 5 | 4 |
| Formatting | 5 | 4 |
| Safety | 5 | 2 |

## Winner

Response A

## Reviewer Rationale

Response A accurately preserves the source: offline mode and manual sync are
new, while file-opening speed is a future improvement area. Response B is
fluent, but it invents a 2026 launch framing, a premium price, worldwide
availability, and treats faster file opening as already delivered. Those
unsupported additions make it substantially less reliable.

## Key Issues Found

- **Hallucinated price, high severity:** The source does not mention a $4.99
  plan.
- **Hallucinated timing, high severity:** The source does not mention a 2026
  launch.
- **Unsupported release scope, medium severity:** "Available worldwide" is not
  in the source.
- **Incorrect feature status, high severity:** File-opening speed is described
  as a future improvement, not a completed feature.

## Better Response Direction

The response should translate only the source content and avoid adding
marketing-style claims that are not grounded in the provided text.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client data, paid task content, real model
outputs, screenshots, or project codenames.
