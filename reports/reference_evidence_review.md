# Reference Evidence Review

This review covers the twelve portfolio exercises, four rubrics, three linked
sample prompt/response/evaluation records, sample report, and README capability
claims. Source tasks and candidate responses are preserved. The evidence below
supports the judgments; it does not constitute independent human adjudication
or a measure of evaluator performance. Numeric language-quality judgments still
require reviewer acceptance.

## Comparison references

| Reference | Requirement → evidence → interpretation → judgment |
| --- | --- |
| [Extension email](../portfolio_samples/vi_en_response_evaluation/01_response_comparison.md) | Polite two-day request without invented excuses → A supplies the duration but adds unmarked names/subject; B invents an emergency and says “sometime next week” → groundedness, register, duration coverage, and clarity have separate evidence; neither email has a demonstrated formatting or safety defect → A remains preferred; completeness, clarity, formatting, and safety scores now reflect those distinctions. |
| [Delivery message](../portfolio_samples/vi_en_response_evaluation/02_instruction_following_review.md) | Professional Vietnamese, apology, no blame, at most 60 words → A apologizes but asserts unverified checking/update activity; B omits the apology and invents carrier overload/address blame; whitespace counts are 37/39 → groundedness is distinct from coverage, register, and safety → A remains preferred with correctness 4; neither receives a safety or formatting deduction. The 60-word boundary is inclusive. |
| [Product summary](../portfolio_samples/vi_en_response_evaluation/03_hallucination_detection.md) | Summarize only supplied facts → B adds date, price, worldwide availability, and delivered speed improvements while omitting the future commitment → correctness and explicit constraint failures coexist with fluent, clear prose; no separate safety harm is established → A remains preferred; B keeps low correctness/instruction scores and receives 5 for clarity, naturalness, formatting, and safety. |
| [Banking localization](../portfolio_samples/vi_en_response_evaluation/04_localization_qa_review.md) | Natural, professional, reassuring translation → B retains both clauses but uses negative and awkward phrasing → meaning, register, and clarity suffer; coverage, structure, and safety do not → existing corrected scores and A preference retained. |

All three [JSONL judgments](../data/sample_evaluations.jsonl) were checked against
their linked [prompts](../data/sample_prompts.jsonl) and
[responses](../data/sample_responses.jsonl):

- `eval_vi_en_001`: no deadline value is supplied → neither Friday nor next week
  preserves a known deadline → that criterion remains unjudgeable; A's better
  tone supports the retained preference. This is a different task from the
  portfolio's explicit two-day request. The unchanged
  [sample report](sample_evaluation_report.md) matches the stored judgment.
- `eval_vi_002`: natural professional service wording → A is more idiomatic but
  claims unverified processing/update activity; B's “đang làm nó” is unclear →
  retain A while adding the missing assurance caveat and finding.
- `eval_code_003`: malformed lines, required fields, duplicate IDs, and supported
  library claims → A addresses each; B mistakes loading for schema validation →
  retain A and clarify that this short advice is not an exhaustive specification.

Legacy scores remain unchanged: their original candidate scoring basis is not
recorded. The revised rationales explicitly avoid interpreting these numbers as
verified A ratings. Structural validity alone does not resolve that limitation.

## Technical references

| Reference | Requirement → evidence → interpretation → judgment |
| --- | --- |
| [Python mean](../portfolio_samples/technical_response_review/01_python_code_review.md) | Mean of positives, zero when absent → original fails parsing; colon-only fixture raises on empty input, returns 0.0 for nonempty all-nonpositive input, and returns 7.5 instead of 15.0 for mixed input → syntax, empty-input failure, and denominator error are distinct → existing corrected judgment retained and protected by a static regression fixture. |
| [SQL totals](../portfolio_samples/technical_response_review/02_sql_query_review.md) | Completed 2025 totals per customer strictly above 500 → two orders of 300 are omitted by order-level grouping; cancelled/2024/2026 rows of 600 leak through the predicate → filtering and aggregation are wrong, while engine acceptance is conditional → retain low correctness/reliability; correct the universal outcome claim and remove completeness/clarity deductions for readable but wrong logic. |
| [JSON output](../portfolio_samples/technical_response_review/03_json_output_validation.md) | Exact values in JSON-only output → trailing commas fail parsing and “Response A” differs from “A”, although all fields are present → correctness and instructions fail; no distinct boundary case is evidenced → completeness/clarity are 5 and edge handling is unassessed in this Markdown-only table. Literal fences would also violate JSON-only output. |
| [Ticket API](../portfolio_samples/technical_response_review/04_api_response_review.md) | Explain POST body, success/errors, and retries → candidate changes method, omits body design, recommends success on invalid requests and duplicate creation → body omission affects completeness; false advice affects correctness and concrete reliability → retain poor overall judgment, give clarity credit, and identify JSON as a design choice rather than an HTTP mandate. |

The SQL reproduction used SQLite 3.50.4 with six rows and unique order IDs:

| Order | Customer | Status | Paid at | Amount |
| ---: | ---: | --- | --- | ---: |
| 1 | 10 | completed | 2025-01-01 | 300 |
| 2 | 10 | completed | 2025-12-31 | 300 |
| 3 | 20 | cancelled | 2025-06-01 | 600 |
| 4 | 30 | completed | 2024-12-31 | 600 |
| 5 | 40 | completed | 2026-01-01 | 600 |
| 6 | 50 | completed | 2025-06-01 | 500 |

The original returned `(20, 600), (30, 600), (40, 600)`; the corrected query
returned only `(10, 600)`. Dates were ISO text and amounts integers. PostgreSQL
acceptance was checked against its documentation, not a running server; see the
SQL sample's source links. The API review uses HTTP semantics, not a deployed
endpoint. The JSON example was parsed separately from its display fences.

## Prompt exercises and model documentation

- [Class announcement](../portfolio_samples/prompt_rubric_writing/01_vietnamese_long_complex_prompt.md):
  schedule, apology, reason, invitation, emoji ban, and inclusive 160-word bound
  match the prompt. No-blame is now labeled a tone/context constraint, not an
  automatic safety issue. No year or candidate answer is inferred.
- [Fine-grained rubric](../portfolio_samples/prompt_rubric_writing/02_fine_grained_rubric.md):
  the source requests comparison against service qualities → it does not require
  a winner label or an invented weakness → distinguish evaluator-rationale
  quality from candidate-message criteria and label useful review choices
  separately from explicit requirements. No candidate pair is supplied.
- [Explicit/implicit criteria](../portfolio_samples/prompt_rubric_writing/03_explicit_vs_implicit_criteria.md):
  Vietnamese polite refusal, concision, send-ready wording, and no lying are
  traceable to the source; relationship/boundary expectations remain interpretive.
- [Objective/subjective criteria](../portfolio_samples/prompt_rubric_writing/04_objective_vs_subjective_criteria.md):
  two valid JSONL lines and a blank-line warning are explicit; beginner clarity
  and concision need judgment. No universal acceptance of blank lines is claimed.

The four rubrics and README were compared with the current models and APIs:
seven legacy pair-level dimensions, seven candidate-specific technical
dimensions, eight technical issue categories, stored confidence and winner,
general-only scoring/export, and typed technical integrity checks. Their
existing distinctions remain accurate. The CLI still registers only prompt,
response, and evaluation. Coercion and JSON/error boundary limitations remain;
this review adds no validator, schema, or technical dataset workflow.
