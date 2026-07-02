# SQL Query Review

## User Prompt

Write a SQL query that returns each customer ID and their total paid order
amount for completed orders in 2025. Include customers only if their total is
greater than 500.

Assume a table:

```sql
orders(order_id, customer_id, status, paid_at, amount)
```

## AI Technical Response

```sql
SELECT customer_id, SUM(amount) AS total_paid
FROM orders
WHERE status = 'completed'
  AND paid_at >= '2025-01-01'
  OR paid_at < '2026-01-01'
GROUP BY order_id
HAVING amount > 500;
```

This gets completed orders in 2025 and filters customers above 500.

## Technical Issues Found

- **Logic error:** `AND ... OR ...` lacks parentheses, so rows before 2026 may
  be included even when status is not completed.
- **Grouping error:** The query groups by `order_id`, not `customer_id`, so it
  does not return totals per customer.
- **HAVING error:** `HAVING amount > 500` checks a raw column instead of the
  aggregate total.
- **Missing date boundary clarity:** The intended range should be
  `paid_at >= '2025-01-01' AND paid_at < '2026-01-01'`.

## Corrected Direction

```sql
SELECT
  customer_id,
  SUM(amount) AS total_paid
FROM orders
WHERE status = 'completed'
  AND paid_at >= '2025-01-01'
  AND paid_at < '2026-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 500;
```

## Rubric Scores

| Criterion | Score | Reviewer note |
| --- | ---: | --- |
| Instruction following | 2 | Attempts the requested fields but groups at the wrong level. |
| Correctness | 1 | Boolean logic, grouping, and aggregate filter are incorrect. |
| Completeness | 3 | Includes status and date ideas but applies them incorrectly. |
| Clarity | 3 | Query is readable, but the explanation overclaims correctness. |
| Edge-case handling | 2 | Boundary dates are present but vulnerable to logic mistakes. |
| Safety/reliability | 2 | Would produce misleading customer totals. |

## Reviewer Rationale

The response is not reliable because it fails the core aggregation requirement.
The reviewer should flag the grouping and `HAVING` problems first, then the
operator-precedence issue because it can silently include the wrong orders.

## Edge Cases

- A customer with two completed 2025 orders totaling more than 500 should
  appear once.
- A cancelled 2025 order should not count.
- A completed order on `2026-01-01` should not count.
- A customer with total exactly 500 should not appear because the prompt says
  greater than 500.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client schemas, paid task content, real
model outputs, screenshots, or project codenames.
