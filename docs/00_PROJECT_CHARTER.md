# Project Charter

> Status: TARGET / PLANNED charter. Current capabilities are listed in
> [`CODEX_MASTER_CONTEXT.md`](../CODEX_MASTER_CONTEXT.md).

## Problem

The current toolkit demonstrates foundational evaluation and technical-QA
skills but does not yet implement the complete professional lifecycle of
benchmark design, disagreement management, calibration, reproducible
experiments, restricted code evaluation, or agent-trajectory analysis.

## Intended users

- AI/LLM evaluation recruiters and technical reviewers;
- multilingual evaluation teams;
- independent evaluators learning rigorous workflows;
- developers who need a small local reference implementation;
- the repository owner using it as a public, NDA-safe portfolio.

## Primary objectives

1. Build a reproducible evaluation domain model.
2. Build a defensible Vietnamese-English benchmark family.
3. Demonstrate independent annotation, disagreement, and adjudication.
4. Calibrate human confidence and LLM judges.
5. Run versioned baseline/candidate experiments with uncertainty.
6. Evaluate code and agents in controlled environments.
7. Make every public claim auditable from repository artifacts.

## Non-goals

- replacing enterprise annotation platforms;
- creating a public leaderboard at launch;
- collecting private platform/client data;
- hosting untrusted code as a public service;
- training foundation models;
- maximizing benchmark size;
- supporting every provider/framework;
- building UI before methodology and APIs stabilize.

## Constraints

- solo maintainer with Codex assistance;
- public repository;
- NDA-safe content;
- modest local compute;
- deterministic CI without paid APIs;
- Windows/WSL-friendly local development;
- Python remains the primary language.

## Design values

- validity over visual polish;
- difficult evidence over easy volume;
- preserved disagreement over hidden consensus;
- reproducibility over one-off demos;
- explicit limitations over inflated claims;
- small composable core over vendor lock-in;
- security boundary before execution capability.

## Stakeholder acceptance

### Recruiter

Can understand the project in 60 seconds and verify concrete evidence.

### Evaluation specialist

Can inspect rubric design, benchmark cards, annotation guidelines, agreement,
calibration, disagreement, and adjudication.

### Software engineer

Can install, test, extend, and review the architecture and future sandbox.

### Security reviewer

Can understand the threat model, execution restrictions, secrets/network
policy, and audit artifacts.

## Success horizon

A credible target v1 is planned over 24 sequencing weeks at approximately
12–15 focused hours/week. The project should ship intermediate, evidence-backed
releases rather than wait for one large launch.
