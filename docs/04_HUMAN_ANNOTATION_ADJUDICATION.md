# Human Annotation and Adjudication Protocol

> Status: TARGET / PLANNED protocol. Independent annotation and adjudication
> are not implemented in the current repository.

## Roles

- **Author:** creates an item and draft rationale.
- **Annotator:** independently evaluates without peer labels.
- **Adjudicator:** resolves disagreement using evidence and rubric.
- **Benchmark owner:** controls revisions and release status.

One person may hold roles on different items but must not label duplicate work
by one person as independent multi-human annotation.

## Annotation record

Capture criterion labels/scores for each candidate, overall preference, major
errors, evidence, confidence, rationale, elapsed time, order shown,
guideline/rubric version, annotator alias, and skipped/uncertain reason.

## Blindness

Where possible, hide model/provider identity, randomize A/B order, avoid author
hints, hide gold/adjudication, and record when blindness is broken.

## Confidence

Use a controlled interpretation:

- 0.50: unresolved;
- 0.60: slight preference;
- 0.70: meaningful uncertainty;
- 0.80: strong judgment;
- 0.90: very strong;
- 0.95: near-certain and reserved for clear evidence.

Confidence is evaluated for calibration, not rewarded for being high.

## Disagreement workflow

1. Lock independent submissions.
2. Compute disagreement fields.
3. Classify cause.
4. Review prompt, candidates, evidence, rubric, and originals.
5. Decide final label, tie/both-bad, defect, insufficient evidence, or rubric
   ambiguity.
6. Preserve all originals.
7. Re-annotate affected holdout items after guideline changes.

Categories include explicit/implicit requirements, factual/temporal evidence,
localization/register, severity, hard-vs-soft criteria, tie boundaries, item
defects, rubric ambiguity, annotator slips, and policy/safety judgment.

## Agreement reporting

Report sample size, missing/skipped labels, raw agreement, exact coefficient
and weighting, confidence intervals where feasible, criterion/slice results,
prevalence, changed items/rubrics, and adjudication rate.

Do not interpret kappa alone. A release is blocked when critical disagreement
is systematic, unexplained, or caused by an invalid construct/rubric—not simply
because disagreement exists.

Release notes distinguish initial independent agreement, post-guideline
holdout agreement, adjudicated gold, and judge agreement.
