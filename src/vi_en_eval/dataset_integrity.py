"""Cross-record integrity checks for typed technical evaluation datasets."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

from vi_en_eval.schemas import PromptRecord, ResponsePairRecord
from vi_en_eval.technical_models import PairwiseTechnicalEvaluation


@dataclass(frozen=True)
class DatasetIntegrityIssue:
    """A relationship problem found across typed dataset records."""

    code: str
    record_type: str
    record_id: str
    field: str
    referenced_id: str | None
    message: str


_RecordT = TypeVar(
    "_RecordT",
    PromptRecord,
    ResponsePairRecord,
    PairwiseTechnicalEvaluation,
)


def _index_records(
    records: Sequence[_RecordT],
    record_type: str,
    issues: list[DatasetIntegrityIssue],
) -> tuple[dict[str, _RecordT], set[str]]:
    records_by_id: dict[str, _RecordT] = {}
    duplicate_ids: set[str] = set()
    record_label = record_type.replace("_", " ")

    for record in records:
        if record.id in records_by_id:
            duplicate_ids.add(record.id)
            issues.append(
                DatasetIntegrityIssue(
                    code="duplicate_id",
                    record_type=record_type,
                    record_id=record.id,
                    field="id",
                    referenced_id=None,
                    message=f"Duplicate {record_label} id '{record.id}'",
                )
            )
            continue

        records_by_id[record.id] = record

    return records_by_id, duplicate_ids


def validate_technical_dataset_integrity(
    prompts: Sequence[PromptRecord],
    response_pairs: Sequence[ResponsePairRecord],
    technical_evaluations: Sequence[PairwiseTechnicalEvaluation],
) -> list[DatasetIntegrityIssue]:
    """Return all duplicate-ID and cross-record reference issues.

    Prompt mismatches are not inferred from duplicated response-pair IDs because
    those references are ambiguous.
    """

    issues: list[DatasetIntegrityIssue] = []
    prompts_by_id, _ = _index_records(prompts, "prompt", issues)
    response_pairs_by_id, duplicate_response_pair_ids = _index_records(
        response_pairs,
        "response_pair",
        issues,
    )
    _index_records(technical_evaluations, "technical_evaluation", issues)

    for response_pair in response_pairs:
        if response_pair.prompt_id not in prompts_by_id:
            issues.append(
                DatasetIntegrityIssue(
                    code="missing_prompt",
                    record_type="response_pair",
                    record_id=response_pair.id,
                    field="prompt_id",
                    referenced_id=response_pair.prompt_id,
                    message=(
                        f"Response pair '{response_pair.id}' references missing prompt "
                        f"'{response_pair.prompt_id}'"
                    ),
                )
            )

    for evaluation in technical_evaluations:
        if evaluation.prompt_id not in prompts_by_id:
            issues.append(
                DatasetIntegrityIssue(
                    code="missing_prompt",
                    record_type="technical_evaluation",
                    record_id=evaluation.id,
                    field="prompt_id",
                    referenced_id=evaluation.prompt_id,
                    message=(
                        f"Technical evaluation '{evaluation.id}' references missing prompt "
                        f"'{evaluation.prompt_id}'"
                    ),
                )
            )

        referenced_response_pair = response_pairs_by_id.get(evaluation.response_pair_id)
        if referenced_response_pair is None:
            issues.append(
                DatasetIntegrityIssue(
                    code="missing_response_pair",
                    record_type="technical_evaluation",
                    record_id=evaluation.id,
                    field="response_pair_id",
                    referenced_id=evaluation.response_pair_id,
                    message=(
                        f"Technical evaluation '{evaluation.id}' references missing response pair "
                        f"'{evaluation.response_pair_id}'"
                    ),
                )
            )
            continue

        if evaluation.response_pair_id in duplicate_response_pair_ids:
            continue

        if evaluation.prompt_id != referenced_response_pair.prompt_id:
            issues.append(
                DatasetIntegrityIssue(
                    code="prompt_reference_mismatch",
                    record_type="technical_evaluation",
                    record_id=evaluation.id,
                    field="response_pair_id",
                    referenced_id=referenced_response_pair.id,
                    message=(
                        f"Technical evaluation '{evaluation.id}' references prompt "
                        f"'{evaluation.prompt_id}', but response pair "
                        f"'{referenced_response_pair.id}' references prompt "
                        f"'{referenced_response_pair.prompt_id}'"
                    ),
                )
            )

    return issues
