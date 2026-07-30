# Calibration, Statistics, and Uncertainty

> Status: TARGET / PLANNED methodology. The current repository does not
> implement agreement, calibration, confidence intervals, or judge metrics.

## Principles

- Item-level paired evidence is primary.
- Report effect sizes and uncertainty, not only point estimates.
- Calibration asks whether confidence matches observed correctness.
- Agreement and calibration are different.
- Automated judges require selective escalation.
- Metrics require a defined construct and sampling frame.

## Human and judge confidence

Represent confidence as probability that a selected label matches adjudicated
gold. Retain a full probability vector for multi-class outcomes when available.

## Calibration outputs

- reliability diagram;
- Brier score;
- log loss when full probabilities are available;
- expected/maximum calibration error as descriptive summaries;
- calibration by slice;
- selective accuracy at coverage thresholds;
- abstention/escalation rate.

Brier score combines calibration and resolution and must not be described as a
pure calibration measure by itself.

## Pairwise comparison

For baseline and candidate on the same items:

- compute item-level deltas;
- use paired bootstrap where justified;
- report 95% intervals;
- report win/tie/loss;
- state practical thresholds;
- report slices and critical failures.

Do not use independent-sample methods for paired outputs.

## Stochastic systems

Store every repetition, separate within-item/model randomness from benchmark
sampling uncertainty, report incomplete/error runs, and never cherry-pick the
best seed.

## Agreement metrics

- Cohen’s kappa: two categorical annotators;
- weighted kappa: ordinal ratings;
- Krippendorff’s alpha: multiple annotators, missing data, or varied scales;
- Spearman/Kendall: rankings;
- ICC only with justified interval-scale assumptions.

Reports state the exact variant, weights, implementation, sample size,
missingness, and prevalence.

## Regression policy example

```yaml
critical_slices:
  - safety
  - security
  - vietnamese_meaning
rules:
  - metric: task_success
    max_allowed_delta: 0.0
    slices: critical_slices
  - metric: pairwise_win_rate
    minimum_lower_ci: 0.50
  - metric: format_pass_rate
    max_allowed_delta: -0.01
budgets:
  p95_latency_ms: 5000
  mean_cost_usd: 0.03
```

This is illustrative, not an implemented configuration. Thresholds must be
justified and versioned by the owning issue.

## Judge bias tests

Use A/B swap consistency, response-length and formatting perturbations,
model-name removal, identical-answer ties, irrelevant-detail injection,
self-preference where applicable, and language/register slices.

## Sample-size discipline

Small benchmarks can demonstrate rigor if limitations are explicit, broad
population claims are avoided, uncertainty is shown, failures inform future
items, test sets are frozen before comparison, and exploratory results are
distinguished from confirmatory results.
