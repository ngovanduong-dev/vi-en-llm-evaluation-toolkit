# Product and Portfolio Presentation

> Status: CURRENT claim policy plus TARGET / PLANNED presentation requirements.

## Reviewer path

The README should answer:

1. What is implemented now?
2. What evaluation problem does it address?
3. What can a reviewer run locally?
4. What evidence supports each claim?
5. Which capabilities are planned and where are the limitations?

## Target proof block

After the owning issues produce evidence, generate rather than hand-edit:

- benchmark item counts by suite/split;
- test and coverage status;
- latest release;
- supported evaluation modes;
- agreement/calibration metrics with dataset/version;
- sandbox/security status;
- reproducibility command.

The current README does not claim unavailable coverage, benchmark, calibration,
sandbox, or release results.

## Target public artifacts

- architecture diagram;
- benchmark and data cards;
- annotation guide;
- disagreement/adjudication report;
- judge calibration report;
- baseline/candidate experiment report;
- restricted code-evaluation report;
- agent trace report;
- limitations and security model;
- changelog and release evidence.

## UI rule

Build UI only after stable APIs and canonical result bundles. UI may browse
items, collect annotations, inspect disagreements and reports, and show traces.
No evaluation logic may exist exclusively in UI.

## Claim-evidence matrix

The planned generated table contains:

| Public claim | Evidence artifact | Version | Verification command |
| --- | --- | --- | --- |

Example mappings are pairwise annotation to an integration test/export,
agreement to metrics tests/report, restricted Python evaluation to policy and
negative tests, and agent trajectory evaluation to trace/scorer/report
evidence. These examples are not current claims.

## CV positioning

Public wording must follow verified artifacts. Before v1, describe the
implemented toolkit and tested evaluation work accurately. Do not adopt titles
that imply calibrated judges, executable sandbox evaluation, or agent
trajectory systems before those releases pass audit.
