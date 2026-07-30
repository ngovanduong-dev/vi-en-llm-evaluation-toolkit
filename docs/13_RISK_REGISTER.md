# Risk Register

> Status: active governance register. Mitigations may be planned and must not be
> read as implemented unless repository evidence exists.

| Risk | Likelihood | Impact | Mitigation | Trigger |
| --- | ---: | ---: | --- | --- |
| Big-bang rewrite breaks the current portfolio | Medium | High | compatibility layers and vertical issues | migration deletes/renames public paths |
| UI precedes methodology | High | Medium | block UI until stable core/result APIs | UI change before core evidence |
| Synthetic samples remain too easy | High | High | challenge composition and independent review | most items have one obvious failure |
| Fake impression of multi-human study | Medium | Critical | explicit human/simulated labels | one person creates “agreement” data |
| LLM judge treated as oracle | High | High | calibration and escalation before use | judge used without validation |
| Overall metrics hide regressions | High | High | item/slice gates and hard constraints | overall improves while critical slice declines |
| Benchmark contamination | Medium | Medium | provenance, versioning, duplicate analysis | suspicious memorization/leakage |
| Broken benchmark tasks | Medium | High | gold/known-wrong validation | gold fails or valid alternatives fail |
| Sandbox escape or secret access | Low | Critical | threat model, isolation, negative tests | host/network access observed |
| Dependency sprawl | High | Medium | dependency policy and ADRs | framework added for a small feature |
| Provider lock-in | Medium | Medium | adapter boundary | provider types enter domain models |
| Unreproducible model snapshots | High | Medium | record IDs/date/config/output replay | provider alias changes |
| Unsupported README metrics | Medium | High | generated claim evidence | unaudited manual number |
| Burnout or scope growth | Medium | High | roadmap gates and non-goals | parallel unfinished subsystems |
| NDA/privacy leak | Low | Critical | synthetic-only and privacy review | content resembles private source |

## GOV-001-specific residual risks

- governance documents may drift from implementation;
- static baseline descriptions may become stale;
- duplicate templates may diverge;
- target language may be mistaken for current capability.

Mitigate these by status labels, one active PR template, issue-scoped updates,
and evidence-backed claims.
