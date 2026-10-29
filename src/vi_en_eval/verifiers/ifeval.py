from __future__ import annotations

import re
import unicodedata
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vi_en_eval._json import decode_json


class IFEvalConstraintSpec(BaseModel):
    """Deterministic hard-constraint specification for verifying LLM responses."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    require_unicode_nfc: bool = Field(
        default=True,
        description="Require precomposed Unicode NFC normalization rather than decomposed NFD combining characters.",
    )
    min_words: int | None = Field(default=None, ge=1)
    max_words: int | None = Field(default=None, ge=1)
    exact_bullet_count: int | None = Field(default=None, ge=0)
    forbidden_phrases: tuple[str, ...] = Field(default_factory=tuple)
    required_keywords: tuple[str, ...] = Field(default_factory=tuple)
    require_markdown_table: bool = Field(default=False)
    require_valid_json_block: bool = Field(default=False)
    required_json_keys: tuple[str, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_constraints(self) -> Self:
        if self.min_words is not None and self.max_words is not None:
            if self.min_words > self.max_words:
                raise ValueError("min_words must not exceed max_words")
        for values in (self.forbidden_phrases, self.required_keywords, self.required_json_keys):
            if any(not value.strip() for value in values):
                raise ValueError("Constraint terms must not be blank")
        return self


class ConstraintViolation(BaseModel):
    """Detailed record of a single constraint violation with quantitative evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    constraint_name: str
    expected: str
    actual: str
    evidence_rationale: str


class IFEvalVerificationReport(BaseModel):
    """Comprehensive verification report with a synthesized evidence-based English rationale."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    passed: bool
    total_checks: int
    passed_checks: int
    score_ratio: float = Field(ge=0.0, le=1.0)
    word_count: int
    is_unicode_nfc: bool
    violations: tuple[ConstraintViolation, ...]
    synthesized_english_rationale: str


_WORD_PATTERN = re.compile(r"\b\w+\b", flags=re.UNICODE)
_BULLET_PATTERN = re.compile(r"^[ \t]*(?:[-*+•]|\d+[.)])[ \t]+\S.*$", flags=re.MULTILINE)
_FENCE_PATTERN = re.compile(
    r"^[ \t]*```([^\n`]*)\n(.*?)^[ \t]*```[ \t]*$", flags=re.MULTILINE | re.DOTALL
)


def _has_markdown_table(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines[1:], start=1):
        cells = [
            cell.strip() for cell in line.strip().removeprefix("|").removesuffix("|").split("|")
        ]
        header = lines[index - 1].strip().removeprefix("|").removesuffix("|").split("|")
        if (
            "|" in line
            and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)
            and len(header) == len(cells)
            and all(cell.strip() for cell in header)
        ):
            return True
    return False


def _normalize_nfc_lower(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


def verify_instruction_following(
    response_text: str,
    spec: IFEvalConstraintSpec,
) -> IFEvalVerificationReport:
    """Verify deterministic formatting and lexical constraints and synthesize an English evaluation rationale."""
    violations: list[ConstraintViolation] = []
    total_checks = 0

    is_nfc = unicodedata.is_normalized("NFC", response_text)
    if spec.require_unicode_nfc:
        total_checks += 1
        if not is_nfc:
            violations.append(
                ConstraintViolation(
                    constraint_name="unicode_nfc_normalization",
                    expected="Strictly NFC-normalized Vietnamese text",
                    actual="Text differs from its NFC normalization",
                    evidence_rationale=(
                        "The response is not Unicode NFC-normalized; NFD sequences are one "
                        "possible cause."
                    ),
                )
            )

    nfc_text = unicodedata.normalize("NFC", response_text).replace("\r\n", "\n").replace("\r", "\n")
    nfc_lower = nfc_text.casefold()
    words = _WORD_PATTERN.findall(nfc_text)
    word_count = len(words)

    if spec.min_words is not None:
        total_checks += 1
        if word_count < spec.min_words:
            violations.append(
                ConstraintViolation(
                    constraint_name="min_words",
                    expected=f">= {spec.min_words} words",
                    actual=f"{word_count} words",
                    evidence_rationale=(
                        f"Failed minimum length constraint: expected at least {spec.min_words} "
                        f"words, but the response contains only {word_count} words."
                    ),
                )
            )

    if spec.max_words is not None:
        total_checks += 1
        if word_count > spec.max_words:
            violations.append(
                ConstraintViolation(
                    constraint_name="max_words",
                    expected=f"<= {spec.max_words} words",
                    actual=f"{word_count} words",
                    evidence_rationale=(
                        f"Exceeded maximum length constraint: expected at most {spec.max_words} "
                        f"words, but the response contains {word_count} words."
                    ),
                )
            )

    if spec.exact_bullet_count is not None:
        total_checks += 1
        bullets = _BULLET_PATTERN.findall(_FENCE_PATTERN.sub("", nfc_text))
        if len(bullets) != spec.exact_bullet_count:
            violations.append(
                ConstraintViolation(
                    constraint_name="exact_bullet_count",
                    expected=f"Exactly {spec.exact_bullet_count} bullet items",
                    actual=f"{len(bullets)} bullet items",
                    evidence_rationale=(
                        f"Failed formatting constraint: requested exactly {spec.exact_bullet_count} "
                        f"bullet points, but found {len(bullets)}."
                    ),
                )
            )

    if spec.forbidden_phrases:
        total_checks += 1
        found_forbidden = [
            phrase
            for phrase in spec.forbidden_phrases
            if _normalize_nfc_lower(phrase) and _normalize_nfc_lower(phrase) in nfc_lower
        ]
        if found_forbidden:
            joined = ", ".join(f"'{p}'" for p in found_forbidden)
            violations.append(
                ConstraintViolation(
                    constraint_name="forbidden_phrases",
                    expected="0 forbidden terms",
                    actual=f"Found: {joined}",
                    evidence_rationale=(
                        f"Violated negative constraint by including forbidden phrase(s): {joined}."
                    ),
                )
            )

    if spec.required_keywords:
        total_checks += 1
        missing_keywords = [
            kw
            for kw in spec.required_keywords
            if _normalize_nfc_lower(kw) and _normalize_nfc_lower(kw) not in nfc_lower
        ]
        if missing_keywords:
            joined = ", ".join(f"'{k}'" for k in missing_keywords)
            violations.append(
                ConstraintViolation(
                    constraint_name="required_keywords",
                    expected=f"Must include all required keywords: {list(spec.required_keywords)}",
                    actual=f"Missing: {joined}",
                    evidence_rationale=(
                        f"Omitted required keyword(s) specified in the prompt: {joined}."
                    ),
                )
            )

    if spec.require_markdown_table:
        total_checks += 1
        if not _has_markdown_table(_FENCE_PATTERN.sub("", nfc_text)):
            violations.append(
                ConstraintViolation(
                    constraint_name="require_markdown_table",
                    expected="Valid Markdown table with header separator row",
                    actual="No valid Markdown table found",
                    evidence_rationale=(
                        "Failed formatting constraint: the response does not contain a valid "
                        "Markdown table."
                    ),
                )
            )

    if spec.require_valid_json_block or spec.required_json_keys:
        total_checks += 1
        # Decode original text so normalization cannot silently change JSON keys.
        candidates = [
            match.group(2)
            for match in _FENCE_PATTERN.finditer(response_text.replace("\r\n", "\n"))
            if match.group(1).strip().casefold() in {"", "json"}
        ]
        raw_json_candidate = candidates[0] if candidates else response_text.strip()
        try:
            if len(candidates) > 1:
                raise ValueError("Multiple JSON blocks are ambiguous")
            parsed_json = decode_json(raw_json_candidate)
            if spec.required_json_keys:
                if not isinstance(parsed_json, dict):
                    violations.append(
                        ConstraintViolation(
                            constraint_name="required_json_keys",
                            expected="JSON object (dict) containing required keys",
                            actual=f"JSON root is {type(parsed_json).__name__}",
                            evidence_rationale=(
                                "Expected a JSON object with specific keys, but the output JSON "
                                "root is not an object."
                            ),
                        )
                    )
                else:
                    missing_keys = [k for k in spec.required_json_keys if k not in parsed_json]
                    if missing_keys:
                        violations.append(
                            ConstraintViolation(
                                constraint_name="required_json_keys",
                                expected=f"Keys present: {list(spec.required_json_keys)}",
                                actual=f"Missing keys: {missing_keys}",
                                evidence_rationale=(
                                    f"The JSON payload is missing required key(s): {missing_keys}."
                                ),
                            )
                        )
        except (ValueError, RecursionError) as exc:
            violations.append(
                ConstraintViolation(
                    constraint_name="require_valid_json_block",
                    expected="Syntactically valid JSON payload",
                    actual=type(exc).__name__,
                    evidence_rationale=(f"The JSON payload failed decoding or selection: {exc}."),
                )
            )

    passed_checks = max(0, total_checks - len(violations))
    score_ratio = round(passed_checks / total_checks, 4) if total_checks > 0 else 1.0
    passed = len(violations) == 0

    if passed:
        rationale = (
            f"The response followed all {total_checks} deterministic instruction constraints "
            f"(word count: {word_count}, Unicode NFC valid: {is_nfc})."
        )
    else:
        bullet_reasons = " ".join(v.evidence_rationale for v in violations)
        rationale = (
            f"The response failed {len(violations)} out of {total_checks} deterministic "
            f"instruction constraints. {bullet_reasons}"
        )

    return IFEvalVerificationReport(
        passed=passed,
        total_checks=total_checks,
        passed_checks=passed_checks,
        score_ratio=score_ratio,
        word_count=word_count,
        is_unicode_nfc=is_nfc,
        violations=tuple(violations),
        synthesized_english_rationale=rationale,
    )
