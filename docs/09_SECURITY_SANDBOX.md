# Security and Sandbox Standard

> Status: governance standard and TARGET controls. The current repository has
> no execution sandbox.

## Principles

- least privilege;
- deny by default;
- approval for boundary crossing;
- isolated execution;
- immutable inputs;
- no secrets in task environments;
- complete audit trail;
- reproducible policy.

## Threat surfaces

- dependency installation;
- future provider adapters;
- generated code;
- future agent shell/tool calls;
- report rendering;
- dataset archives;
- CI tokens;
- local environment files.

## Development-agent controls

- operate in the version-controlled workspace;
- restrict network where practical;
- require approval for destructive/high-risk commands;
- keep credentials outside the repository;
- preserve tool/approval logs where available.

## Future evaluation-sandbox controls

- no outbound network;
- non-root user;
- resource limits;
- read-only root where practical;
- ephemeral workdir;
- no privileged mode, host socket, or device;
- pinned image;
- timeout/cleanup;
- logs and state diff.

## CI controls

- least-privilege GitHub permissions;
- documented action pinning policy;
- no secrets for untrusted pull requests;
- dependency auditing and code scanning when their issues land;
- artifact retention without private data.

## Secrets

- `.env*` ignored;
- sample config uses placeholders;
- API tests opt-in;
- logs redact credentials;
- no model output containing private work;
- rotate immediately if a secret is committed.

## Threat-model template

For executable features record assets, actors, trust boundaries, entry points,
abuse cases, mitigations, residual risk, tests, and approval owner.

## Incident response

If a sandbox escape, secret exposure, or private-data leak is suspected:

1. stop execution;
2. preserve logs;
3. rotate affected credentials;
4. remove public exposure;
5. identify affected commits/artifacts;
6. document root cause;
7. add regression coverage;
8. publish an appropriate security note without unnecessary exploit detail.

See [`SECURITY.md`](../SECURITY.md) for reporting guidance.
