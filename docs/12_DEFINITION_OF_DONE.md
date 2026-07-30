# Definition of Done

> Status: governance gates. Apply only gates relevant to the issue/release;
> target subsystem gates do not imply those subsystems exist.

## Issue-level DoD

- acceptance criteria satisfied;
- positive, negative, boundary, and failure-path validation as applicable;
- every currently configured check passes;
- docs and changelog updated;
- migration/backwards compatibility addressed;
- security/privacy/NDA impact reviewed;
- no unsupported public claim;
- exact command results reported.

## Milestone-level DoD

- clean-install reproduction;
- tagged release only when authorized and ready;
- immutable sample artifacts;
- current architecture/methodology;
- no unresolved critical security/quality issue;
- known limitations;
- migration from previous behavior tested;
- claim-evidence matrix when its issue lands.

## Benchmark release DoD

- card and manifest;
- provenance/license;
- schema/integrity and gold/oracle validation;
- independent pilot labels;
- disagreement/adjudication and agreement reports;
- slices and contamination note;
- defects/exclusions;
- frozen version/hash.

## Judge release DoD

- separate calibration set;
- human-adjudicated gold;
- bias probes;
- confidence calibration;
- selective escalation;
- cost/latency;
- versioned prompt/config;
- failure examples and limitations.

## Code-evaluation DoD

- threat model and restricted sandbox;
- gold and known-wrong validation;
- hidden/executable tests;
- timeout/resource behavior;
- logs/artifacts;
- deterministic clean run;
- no host secret/network exposure.

## Agent-evaluation DoD

- controlled tools;
- trace/replay;
- final-state oracle;
- trajectory evidence;
- failure injection;
- policy/side-effect checks;
- cost/latency/steps;
- offline CI.

## v1.0 DoD

A fresh reviewer can complete the success actions in
[`CODEX_MASTER_CONTEXT.md`](../CODEX_MASTER_CONTEXT.md) using documented
commands. Public claims resolve to evidence, and synthetic portfolio evidence
is clearly distinguished from paid experience.
