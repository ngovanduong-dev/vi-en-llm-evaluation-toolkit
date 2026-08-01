# Security Policy

## Current security boundary

The implemented repository validates structured records and parses Python
syntax. It does **not** provide a restricted execution sandbox and must not be
used to execute untrusted generated code.

Any future execution capability must undergo security review and use
appropriate isolation before it is enabled. A planned execution capability
must not be described as a current repository feature.

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
