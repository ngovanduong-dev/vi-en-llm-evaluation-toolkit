"""Load and validate linked technical evaluation JSONL datasets."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel

from vi_en_eval.dataset_integrity import (
    DatasetIntegrityIssue,
    validate_technical_dataset_integrity,
)
from vi_en_eval.jsonl_validator import ValidationIssue, _load_typed_jsonl
from vi_en_eval.schemas import PromptRecord, ResponsePairRecord
from vi_en_eval.technical_models import PairwiseTechnicalEvaluation

RecordType = Literal["prompt", "response_pair", "technical_evaluation"]


@dataclass(frozen=True)
class TechnicalDataset:
    """A complete linked dataset whose records and relationships are valid."""

    prompts: tuple[PromptRecord, ...]
    response_pairs: tuple[ResponsePairRecord, ...]
    technical_evaluations: tuple[PairwiseTechnicalEvaluation, ...]


@dataclass(frozen=True)
class TechnicalDatasetFileResult:
    """Validation counts for one collection file."""

    record_type: RecordType
    file_path: str
    total_lines: int | None
    valid_records: int | None


@dataclass(frozen=True)
class TechnicalDatasetIssue:
    """A deterministic file, record, or relationship diagnostic."""

    code: str
    record_type: RecordType
    file_path: str
    message: str
    line_number: int | None = None
    field: str | None = None
    record_id: str | None = None
    referenced_id: str | None = None


@dataclass(frozen=True)
class TechnicalDatasetLoadResult:
    """Outcome of loading and validating three linked collection files."""

    files: tuple[TechnicalDatasetFileResult, ...]
    issues: tuple[TechnicalDatasetIssue, ...]
    integrity_checked: bool
    dataset: TechnicalDataset | None

    @property
    def is_valid(self) -> bool:
        """Return whether a complete typed dataset is available."""

        return self.dataset is not None and not self.issues

    def to_dict(self) -> dict[str, Any]:
        """Serialize diagnostics and counts without serializing candidate content."""

        return {
            "is_valid": self.is_valid,
            "integrity_checked": self.integrity_checked,
            "files": [asdict(file_result) for file_result in self.files],
            "issues": [asdict(issue) for issue in self.issues],
        }


_RecordT = TypeVar("_RecordT", bound=BaseModel)


@dataclass(frozen=True)
class _CollectionLoad(Generic[_RecordT]):
    file_result: TechnicalDatasetFileResult
    records: tuple[_RecordT, ...]
    issues: tuple[TechnicalDatasetIssue, ...]


def _file_issue(
    record_type: RecordType,
    file_path: str,
    code: str,
    message: str,
) -> _CollectionLoad[Any]:
    return _CollectionLoad(
        file_result=TechnicalDatasetFileResult(
            record_type=record_type,
            file_path=file_path,
            total_lines=None,
            valid_records=None,
        ),
        records=(),
        issues=(
            TechnicalDatasetIssue(
                code=code,
                record_type=record_type,
                file_path=file_path,
                message=message,
            ),
        ),
    )


def _convert_validation_issue(
    issue: ValidationIssue,
    record_type: RecordType,
    file_path: str,
) -> TechnicalDatasetIssue:
    return TechnicalDatasetIssue(
        code=issue.code,
        record_type=record_type,
        file_path=file_path,
        line_number=issue.line_number,
        field=issue.field,
        message=issue.message,
    )


def _load_collection(
    path: str | Path,
    record_type: RecordType,
    model: type[_RecordT],
) -> _CollectionLoad[_RecordT]:
    file_path = str(Path(path))
    try:
        loaded = _load_typed_jsonl(path, record_type, model, collect_records=True)
    except UnicodeDecodeError:
        return _file_issue(
            record_type,
            file_path,
            "invalid_utf8",
            "Input is not valid UTF-8",
        )
    except OSError:
        return _file_issue(
            record_type,
            file_path,
            "file_read_error",
            "Unable to read input file",
        )

    validation = loaded.validation
    return _CollectionLoad(
        file_result=TechnicalDatasetFileResult(
            record_type=record_type,
            file_path=validation.file_path,
            total_lines=validation.total_lines,
            valid_records=validation.valid_records,
        ),
        records=loaded.records,
        issues=tuple(
            _convert_validation_issue(issue, record_type, validation.file_path)
            for issue in validation.issues
        ),
    )


def _convert_integrity_issue(
    issue: DatasetIntegrityIssue,
    file_paths: Mapping[RecordType, str],
) -> TechnicalDatasetIssue:
    if issue.record_type == "prompt":
        record_type: RecordType = "prompt"
    elif issue.record_type == "response_pair":
        record_type = "response_pair"
    elif issue.record_type == "technical_evaluation":
        record_type = "technical_evaluation"
    else:
        raise ValueError(f"Unsupported integrity record type: {issue.record_type}")
    return TechnicalDatasetIssue(
        code=issue.code,
        record_type=record_type,
        file_path=file_paths[record_type],
        field=issue.field,
        record_id=issue.record_id,
        referenced_id=issue.referenced_id,
        message=issue.message,
    )


def load_technical_dataset(
    prompts_path: str | Path,
    response_pairs_path: str | Path,
    technical_evaluations_path: str | Path,
) -> TechnicalDatasetLoadResult:
    """Load typed records and validate their links as one technical dataset.

    Relationship checks run only after all files pass transport, schema, and
    duplicate-ID validation. This prevents missing-link errors caused solely by
    dropping malformed rows.
    """

    prompts = _load_collection(prompts_path, "prompt", PromptRecord)
    response_pairs = _load_collection(
        response_pairs_path,
        "response_pair",
        ResponsePairRecord,
    )
    evaluations = _load_collection(
        technical_evaluations_path,
        "technical_evaluation",
        PairwiseTechnicalEvaluation,
    )
    collections = (prompts, response_pairs, evaluations)
    files = tuple(collection.file_result for collection in collections)
    file_issues = tuple(issue for collection in collections for issue in collection.issues)

    if file_issues:
        return TechnicalDatasetLoadResult(
            files=files,
            issues=file_issues,
            integrity_checked=False,
            dataset=None,
        )

    candidate_dataset = TechnicalDataset(
        prompts=prompts.records,
        response_pairs=response_pairs.records,
        technical_evaluations=evaluations.records,
    )
    file_paths = {file_result.record_type: file_result.file_path for file_result in files}
    integrity_issues = tuple(
        _convert_integrity_issue(issue, file_paths)
        for issue in validate_technical_dataset_integrity(
            candidate_dataset.prompts,
            candidate_dataset.response_pairs,
            candidate_dataset.technical_evaluations,
        )
    )
    return TechnicalDatasetLoadResult(
        files=files,
        issues=integrity_issues,
        integrity_checked=True,
        dataset=None if integrity_issues else candidate_dataset,
    )


def format_technical_dataset_result(result: TechnicalDatasetLoadResult) -> str:
    """Format a concise human-readable dataset result."""

    status = "VALID" if result.is_valid else "INVALID"
    lines = [f"{status}: technical dataset"]
    for file_result in result.files:
        count = (
            "unavailable"
            if file_result.valid_records is None or file_result.total_lines is None
            else f"{file_result.valid_records}/{file_result.total_lines} records"
        )
        lines.append(f"- {file_result.record_type}: {count} ({file_result.file_path})")
    lines.append("Integrity: checked" if result.integrity_checked else "Integrity: not checked")
    if result.issues:
        lines.append("Issues:")
        for issue in result.issues:
            location: str = issue.record_type
            if issue.line_number is not None:
                location += f" line {issue.line_number}"
            field = f" [{issue.field}]" if issue.field else ""
            lines.append(f"- {location}: {issue.code}{field}: {issue.message}")
    return "\n".join(lines)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the technical dataset command parser."""

    parser = argparse.ArgumentParser(
        description="Validate three linked technical evaluation JSONL collections."
    )
    parser.add_argument("--prompts", required=True, help="Path to prompt records JSONL.")
    parser.add_argument(
        "--responses",
        required=True,
        help="Path to response-pair records JSONL.",
    )
    parser.add_argument(
        "--evaluations",
        required=True,
        help="Path to pairwise technical evaluation records JSONL.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run linked technical dataset validation."""

    args = create_argument_parser().parse_args(argv)
    result = load_technical_dataset(args.prompts, args.responses, args.evaluations)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(format_technical_dataset_result(result))
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
