# Portfolio Samples

**Synthetic-only note:** All portfolio samples in this directory must be
original, synthetic, and public-safe. Do not add private platform tasks,
internal guidelines, paid task content, real model outputs, client data,
screenshots, project codenames, or materials copied from work queues.

This directory is the human-readable portfolio layer for the
Vietnamese-English LLM Evaluation Toolkit. It complements the machine-readable
sample data, rubrics, validation code, tests, and exported reports already in
the repository.

## Purpose

The portfolio samples should help AI recruiters, platform reviewers, and
technical reviewers quickly see evaluator judgment in action:

- Comparing two AI responses against the same prompt.
- Applying rubric scores and selecting a winner.
- Writing concise reviewer rationales.
- Identifying hallucination, localization, tone, safety, and instruction
  following issues.
- Reviewing coding and structured-output responses for technical quality.

## Planned Categories

| Category | Planned path | Demonstrates | Tracking |
| --- | --- | --- | --- |
| Vietnamese-English response evaluation | `portfolio_samples/vi_en_response_evaluation/` | Response comparison, instruction following, hallucination detection, localization QA | `#20` |
| Prompt and rubric writing | `portfolio_samples/prompt_rubric_writing/` | Vietnamese prompt design, explicit and implicit criteria, atomic rubric writing | `#21` |
| Synthetic personalization evaluation | `portfolio_samples/personalization_evaluation_synthetic/` | Fake-profile personalization review, missing personalization, unsupported inference, privacy-safe reasoning | Future issue |
| Technical response review | `portfolio_samples/technical_response_review/` | Python, SQL, JSON, API explanation review, edge cases, unsupported technical claims | `#22` |

## Available Samples

### Vietnamese-English Response Evaluation

- [Vietnamese-English response comparison](vi_en_response_evaluation/01_response_comparison.md)
- [Instruction-following review](vi_en_response_evaluation/02_instruction_following_review.md)
- [Hallucination detection review](vi_en_response_evaluation/03_hallucination_detection.md)
- [Vietnamese localization QA review](vi_en_response_evaluation/04_localization_qa_review.md)

### Prompt and Rubric Writing

- [Vietnamese long complex prompt](prompt_rubric_writing/01_vietnamese_long_complex_prompt.md)
- [Fine-grained rubric](prompt_rubric_writing/02_fine_grained_rubric.md)
- [Explicit vs implicit criteria](prompt_rubric_writing/03_explicit_vs_implicit_criteria.md)
- [Objective vs subjective criteria](prompt_rubric_writing/04_objective_vs_subjective_criteria.md)

### Technical Response Review

- [Python code review](technical_response_review/01_python_code_review.md)
- [SQL query review](technical_response_review/02_sql_query_review.md)
- [JSON output validation review](technical_response_review/03_json_output_validation.md)
- [REST API explanation review](technical_response_review/04_api_response_review.md)

## Sample Quality Standard

Each sample should be:

- Synthetic and original.
- Realistic enough to resemble public AI evaluation workflows.
- Specific about the prompt constraints being evaluated.
- Clear about why one response is stronger, weaker, incomplete, unsafe, or
  misaligned.
- Grounded in atomic, self-contained rubric criteria.
- Explicit about failure modes such as missing constraints, hallucinated facts,
  unnatural localization, invalid JSON, syntax errors, or unsupported API
  claims.

Avoid generic rationales such as:

```text
Response A is better because it is more detailed.
The answer is good.
The model should be more accurate.
```

Prefer rationale wording like:

```text
Response A wins because it preserves the user's requested formal Vietnamese
tone, keeps all three constraints, and avoids adding unsupported facts.
Response B is fluent but invents a deadline and omits the requested comparison
table.
```

## Suggested Sample Template

Use this structure unless a sample type needs a more specific format:

```md
# Sample Title

## Task Type
## User Prompt
## Response A
## Response B
## Evaluation Criteria
## Rubric Scores
## Winner
## Reviewer Rationale
## Key Issues Found
## Better Response Direction
## Confidentiality Note
```

## Reviewer Paths

For AI recruiters and platform reviewers:

```text
README
-> portfolio_samples/README.md
-> selected synthetic sample
-> reports/sample_evaluation_report.md
```

For technical reviewers:

```text
README
-> src/
-> tests/
-> data/*.jsonl
-> reports/sample_evaluation_report.md
```

## What Never Belongs Here

- Real platform prompts, responses, rubrics, screenshots, or task metadata.
- Internal project guidelines or copied guideline phrasing.
- Client names, private repository code, private API examples, or work queue
  content.
- Real model outputs from paid tasks.
- Claims that a sample is based on a private task, even if details are removed.

Public samples should demonstrate the same skill category through original,
generalized, synthetic examples.

## Current Status

The Vietnamese-English response evaluation, prompt/rubric writing, and
technical response review categories now have synthetic samples. Additional
categories will be added in small follow-up PRs so each group can be reviewed
for quality, specificity, and confidentiality.

**Synthetic-only note:** This directory is for original portfolio-safe examples
only. It must not contain private platform data, internal guidelines, client
materials, paid task content, real model outputs, screenshots, or project
codenames.
