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

- **Logic error:** The predicate is `(completed AND lower_bound) OR upper_bound`.
  It admits rows before 2026 regardless of status or the lower bound, and
  completed rows from 2026 onward. Parentheses alone cannot repair the `OR`;
  both date bounds and status must hold.
- **Grouping error:** The query groups by `order_id`, not `customer_id`, so it
  does not return totals per customer.
- **HAVING error:** `HAVING amount > 500` refers to an unaggregated column,
  not the required customer total. Whether this is accepted depends on the
  SQL dialect and declared keys.
- **Missing date boundary clarity:** The intended range should be
  `paid_at >= '2025-01-01' AND paid_at < '2026-01-01'`.

## Discriminating Evidence

The source specifies no dialect, types, or keys. PostgreSQL rejects ungrouped
columns unless an applicable functional dependency exists; an `order_id`
primary key can change acceptance. SQLite permits bare columns. Therefore, do
not claim the original query necessarily returns rows on every engine. See
[PostgreSQL grouping rules](https://www.postgresql.org/docs/current/sql-select.html#SQL-GROUPBY)
and [SQLite bare columns](https://www.sqlite.org/lang_select.html#bareagg).

A controlled SQLite check used unique order IDs, integer amounts, and ISO date
text. Two completed orders for customer 10, dated `2025-01-01` and `2025-12-31`,
with amounts 300 each, should yield `(10, 600)`. The original yields no rows:
its order-level groups each fail `amount > 500`. Separately, single orders of
600 for a cancelled customer in 2025, a completed customer in 2024, and a
completed customer on `2026-01-01` all pass the original predicate but should
be excluded. A completed 2025 customer totaling exactly 500 is correctly
excluded by the corrected strict threshold.

These cases distinguish aggregation, date/status filtering, and threshold
behavior. They are evidence under the stated SQLite assumptions, not a claim
of portable execution. Correctness concerns the wrong selection and totals;
reliability concerns query rejection or downstream use of those wrong totals.

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
| Completeness | 5 | Addresses fields, status, dates, grouping, and threshold; their implementation is wrong. |
| Clarity | 5 | Query and explanation are readable; false claims are penalized under correctness. |
| Edge-case handling | 2 | Boundary dates are present but vulnerable to logic mistakes. |
| Safety/reliability | 2 | May be rejected; if accepted, can omit qualifying customers and include invalid orders. |

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
