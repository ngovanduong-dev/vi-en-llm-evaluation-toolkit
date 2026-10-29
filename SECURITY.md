# Security Policy

## Current security boundary

The dataset validators and evaluator comparison commands never execute response
content. The separate `vi-en-grade grade-ab` command and `run_in_python_sandbox`
API execute explicitly supplied Python source and fixtures in a child process.
Use this capability only for reviewed code in a disposable environment.

The AST policy, clean environment, temporary working directory, bounded output,
and timeout reduce accidental exposure and runaway execution. They do **not**
provide an OS security boundary. The child retains the host account's filesystem
and network permissions, and there are no memory, disk, CPU, or descendant-process
quotas. Python introspection and allowed library behavior cannot be secured by
this syntactic gate. Custom policies can further weaken the restrictions.

Adversarial or unreviewed generated code requires external isolation with
restricted filesystem mounts, disabled network access, resource limits, and
process-tree cleanup. This repository does not provision that environment.
Runtime success means only that the supplied fixture program completed without
an exception; it does not establish test completeness or general correctness.

## Reporting a vulnerability

Do not include secrets, private client material, personal data, or working
exploit details in a public issue.

When GitHub private vulnerability reporting is available, use the repository's
private security-advisory channel. Otherwise, contact the maintainer through
the contact method published on the repository owner's GitHub profile and share
only the minimum information needed to establish a private reporting channel.

Include:

- affected commit/version;
- affected component;
- impact and prerequisites;
- minimal reproduction steps;
- whether secrets or private data may be exposed;
- suggested mitigation, if known.

## Handling

For a suspected secret exposure, private-data leak, or sandbox escape:

1. stop the affected workflow;
2. preserve relevant logs without republishing sensitive data;
3. revoke or rotate affected credentials;
4. remove public exposure where possible;
5. identify affected commits and artifacts;
6. document root cause and residual risk;
7. add a regression test before declaring remediation complete.
