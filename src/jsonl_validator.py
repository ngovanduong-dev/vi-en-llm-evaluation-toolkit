"""JSONL validation utilities for synthetic LLM evaluation datasets."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.schemas import SCHEMA_REGISTRY


@dataclass(frozen=True)
class ValidationIssue:
    """A validation problem found in a JSONL file."""

    line_number: int
    code: str
    message: str
    field: str | None = None


@dataclass(frozen=True)
class JsonlValidationResult:
    """Summary returned by the JSONL validator."""

    file_path: str
    schema_name: str
    total_lines: int
    valid_records: int
    issues: list[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "schema_name": self.schema_name,
            "total_lines": self.total_lines,
            "valid_records": self.valid_records,
            "is_valid": self.is_valid,
            "issues": [asdict(issue) for issue in self.issues],
        }


def _field_path(error_location: tuple[Any, ...]) -> str:
    return ".".join(str(part) for part in error_location)


def _schema_issue(line_number: int, error: dict[str, Any]) -> ValidationIssue:
    field = _field_path(error.get("loc", ()))
    return ValidationIssue(
        line_number=line_number,
        code="schema_validation_error",
        field=field or None,
        message=error.get("msg", "Invalid record"),
    )


def validate_jsonl(path: str | Path, schema_name: str = "evaluation") -> JsonlValidationResult:
    """Validate a JSONL file against one of the registered Pydantic schemas."""

    file_path = Path(path)
    if schema_name not in SCHEMA_REGISTRY:
        allowed = ", ".join(sorted(SCHEMA_REGISTRY))
        raise ValueError(f"Unknown schema '{schema_name}'. Expected one of: {allowed}")

    model = SCHEMA_REGISTRY[schema_name]
    issues: list[ValidationIssue] = []
    total_lines = 0
    valid_records = 0

    with file_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            total_lines += 1
            line = raw_line.strip()

            if not line:
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="blank_line",
                        message="JSONL files should not contain blank lines",
                    )
                )
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="malformed_json",
                        message=f"{exc.msg} at column {exc.colno}",
                    )
                )
                continue

            try:
                model.model_validate(payload)
            except ValidationError as exc:
                issues.extend(_schema_issue(line_number, error) for error in exc.errors())
                continue

            valid_records += 1

    return JsonlValidationResult(
        file_path=str(file_path),
        schema_name=schema_name,
        total_lines=total_lines,
        valid_records=valid_records,
        issues=issues,
    )


def format_validation_result(result: JsonlValidationResult) -> str:
    """Format validator output for CLI use."""

    status = "VALID" if result.is_valid else "INVALID"
    lines = [
        f"{status}: {result.file_path}",
        f"Schema: {result.schema_name}",
        f"Valid records: {result.valid_records}/{result.total_lines}",
    ]

    if result.issues:
        lines.append("Issues:")
        for issue in result.issues:
            field = f" [{issue.field}]" if issue.field else ""
            lines.append(f"- line {issue.line_number}: {issue.code}{field}: {issue.message}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate synthetic LLM evaluation JSONL files.")
    parser.add_argument("path", help="Path to the JSONL file to validate.")
    parser.add_argument(
        "--schema",
        default="evaluation",
        choices=sorted(SCHEMA_REGISTRY),
        help="Schema to validate against.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args(argv)

    result = validate_jsonl(args.path, schema_name=args.schema)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(format_validation_result(result))
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
