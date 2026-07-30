# Production-Style Agent Evaluation

> Status: TARGET / PLANNED. The current repository has no agent runtime,
> controlled tool fixtures, trace model, replay, or trajectory scorers.

## Core distinction

An agent can reach the right final state through an unsafe path, follow a
reasonable path but fail because a tool is defective, or sound fluent while
leaving the environment wrong. Score outcome, trajectory, and environment
effects separately.

## Trace model

Each planned event records identity/parent, timestamp/duration, actor/role,
message or tool call, arguments, result/error, state diff, approval/network/
sandbox decision, usage/cost, policy flags, and artifact references.

## Controlled tools

Initial targets are sandboxed file operations, allowlisted shell, fixed local
search corpus, deterministic calculator, database fixture, synthetic mock
calendar/email where justified, and failure injection. CI must not depend on
open internet.

## Outcome scorers

- final answer correctness;
- file/database final state;
- required artifact content;
- constraints;
- absence of prohibited side effects;
- user-facing communication.

## Trajectory scorers

- relevant tool selection;
- valid arguments and ordering;
- recovery after errors;
- no excessive repetition or unauthorized access;
- state consistency;
- cost/latency/step efficiency;
- appropriate escalation.

## Experimental scanners

Scanners may flag evaluation awareness, reward hacking, test tampering, prompt
injection following, secret access, excessive retries, or final-answer/trace
mismatch. Flags provide evidence; they do not prove intent.

## Task definition

Each task defines initial state, available tools/permissions, desired final
state, forbidden effects, injected failure, outcome/trajectory rubrics,
time/step budget, and replay fixture.

## Comparison

Report success, critical side effects, trajectory quality, recovery,
cost/latency/steps, failure taxonomy, paired uncertainty, and trace examples.
Do not collapse all components into one score without preserving them.
