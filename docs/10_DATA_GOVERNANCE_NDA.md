# Data Governance and NDA Safety

> Status: CURRENT policy for repository content. Manifest enforcement and
> versioned data registries are TARGET / PLANNED.

## Allowed sources

- original human-authored synthetic examples;
- procedurally generated examples;
- permissively licensed public datasets;
- public standards/documentation within license limits;
- original synthetic recreations of general failure categories.

## Prohibited content

- private paid AI platform or client tasks/outputs;
- internal rubrics, guidelines, or project names;
- client data, private code, or queue metadata;
- screenshots or hidden model identity from paid work;
- copied prompts with superficial redaction;
- personal/sensitive data without permission;
- content with unverifiable ownership or licensing.

## Required provenance for future datasets

Every dataset/benchmark manifest records source type, author/owner, public URL
or synthetic identifier, license, retrieval/access date, transformation,
privacy review, contamination risk, and release permission.

## Synthetic labeling

Use explicit labels:

- `original_human_synthetic`;
- `programmatic_synthetic`;
- `model_generated_synthetic`;
- `public_licensed`;
- `derived_public`.

Do not call synthetic annotations real production labels.

## Public/private separation

```text
data/             committed public examples currently live here
data/private/     ignored; never committed
artifacts/local/  ignored; never committed
```

Future issues may introduce more specific public/example paths. Publish schemas
and methodology for hidden data, never hidden answers.

## Retention

- keep released versions immutable;
- deprecate rather than silently rewrite;
- document deletion/withdrawal;
- store only necessary metadata;
- remove direct identifiers.

## Claim policy

The repository may demonstrate transferable evaluation skills. It must not
claim that synthetic samples are paid deliverables or imply affiliation with a
private platform or client.
