# REST API Explanation Review

## User Prompt

Explain how to design a `POST /tickets` endpoint for creating support tickets.
Mention the expected request body, success status code, validation errors, and
idempotency considerations. Keep the explanation concise.

## AI Technical Response

Use `GET /tickets` to create a new ticket because GET is simpler to test. Send
the title and description in query parameters. The API should always return
`200 OK`, even when required fields are missing, because clients can read the
message. If the user retries, create a new ticket every time so no request is
lost.

## Technical Issues Found

- **HTTP method misuse:** Creating a resource should use `POST /tickets`, not
  `GET /tickets`.
- **Request body issue:** Title and description should be in a JSON body, not
  query parameters for resource creation.
- **Validation handling error:** Missing required fields should return a 4xx
  validation error, commonly `400` or `422`, not always `200 OK`.
- **Idempotency risk:** Blind retries can create duplicate tickets; the answer
  ignores idempotency keys or duplicate-request handling.
- **Unsupported simplification:** "GET is simpler to test" is not a valid
  reason to change endpoint semantics.

## Corrected Direction

A better answer should describe `POST /tickets` with a JSON body such as
`title`, `description`, and optional `priority`. On success, the endpoint can
return `201 Created` with the new ticket ID. Validation failures should return
a 4xx response with field-level errors. For retries, the design should consider
an idempotency key or another duplicate-prevention strategy when clients may
resubmit the same create request.

## Rubric Scores

| Criterion | Score | Reviewer note |
| --- | ---: | --- |
| Instruction following | 1 | Changes the requested endpoint method and omits key design requirements. |
| Correctness | 1 | Misstates HTTP semantics and validation behavior. |
| Completeness | 2 | Mentions fields and retries, but in a harmful direction. |
| Clarity | 3 | The explanation is readable but misleading. |
| Edge-case handling | 1 | Retry behavior creates duplicates. |
| Safety/reliability | 1 | Encourages API design that can break clients and data integrity. |

## Reviewer Rationale

This response should be rated poor because it reverses core REST semantics and
creates reliability risks. The most severe issue is recommending `GET` for
resource creation, followed by returning `200 OK` for validation failures and
creating duplicate tickets on retries.

## Edge Cases

- Missing `title` should return a validation error rather than `200 OK`.
- Retrying the same request after a timeout should not necessarily create two
  tickets.
- Query parameters can expose or mangle long descriptions; JSON body input is
  more appropriate.
- Clients may depend on `201 Created` or a returned ticket ID for workflow
  continuation.

## Confidentiality Note

This sample is fully synthetic and portfolio-safe. It does not contain private
platform tasks, internal guidelines, client API designs, paid task content, real
model outputs, screenshots, or project codenames.
