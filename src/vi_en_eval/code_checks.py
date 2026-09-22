"""Basic checks for AI-generated coding responses."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from io import StringIO

from vi_en_eval._json import JsonPolicyError, decode_json

CODING_REVIEW_CHECKLIST = [
    "Syntax error",
    "Logic error",
    "Missing edge case",
    "Runtime risk",
    "API misuse",
    "Unsupported library/function claim",
    "Inefficient solution",
    "Missing explanation",
    "Invalid JSON output",
]


@dataclass(frozen=True)
class CheckResult:
    """Result returned by a lightweight code or structured-output check."""

    is_valid: bool
    code: str
    message: str
    line_number: int | None = None
    column: int | None = None


def check_python_syntax(source: str) -> CheckResult:
    """Check whether a Python snippet can be parsed by the AST parser."""

    try:
        ast.parse(source)
    except SyntaxError as exc:
        return CheckResult(
            is_valid=False,
            code="python_syntax_error",
            message=f"Python syntax error: {exc.msg}.",
            line_number=exc.lineno,
            column=exc.offset,
        )

    return CheckResult(
        is_valid=True,
        code="valid_python_syntax",
        message="Python syntax is valid.",
    )


def validate_json_text(value: str) -> CheckResult:
    """Check JSON syntax, rejecting non-finite literals and duplicate object names."""

    try:
        decode_json(value)
    except JsonPolicyError as exc:
        return CheckResult(is_valid=False, code=exc.code, message=str(exc))
    except json.JSONDecodeError as exc:
        return CheckResult(
            is_valid=False,
            code="invalid_json",
            message=f"Invalid JSON: {exc.msg}.",
            line_number=exc.lineno,
            column=exc.colno,
        )

    return CheckResult(
        is_valid=True,
        code="valid_json",
        message="JSON is valid.",
    )


def validate_jsonl_text(value: str) -> list[CheckResult]:
    """Validate physical JSONL lines (LF, CRLF, or CR); reject blank lines."""

    results: list[CheckResult] = []

    for line_number, line in enumerate(StringIO(value, newline=None), start=1):
        if not line.strip():
            results.append(
                CheckResult(
                    is_valid=False,
                    code="blank_jsonl_line",
                    message="Blank line is not valid JSONL.",
                    line_number=line_number,
                )
            )
            continue

        result = validate_json_text(line.rstrip("\r\n"))
        if result.is_valid:
            results.append(
                CheckResult(
                    is_valid=True,
                    code="valid_jsonl_line",
                    message="JSONL line is valid.",
                    line_number=line_number,
                )
            )
            continue

        results.append(
            CheckResult(
                is_valid=False,
                code=result.code,
                message=result.message,
                line_number=line_number,
                column=result.column,
            )
        )

    return results
