"""Core data models for synthetic LLM evaluation records."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, TypeAlias

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _reject_blank_string(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be blank")
    return value


NonBlankStr: TypeAlias = Annotated[
    str,
    Field(min_length=1),
    AfterValidator(_reject_blank_string),
]


class Language(str, Enum):  # noqa: UP042 - preserve existing Enum string behavior
    """Supported evaluation language modes."""

    VIETNAMESE = "Vietnamese"
    ENGLISH = "English"
    BILINGUAL = "Bilingual"


class TaskType(str, Enum):  # noqa: UP042 - preserve existing Enum string behavior
    """Common task families for LLM evaluation work."""

    GENERAL = "General"
    TRANSLATION = "Translation"
    CODING = "Coding"
    SAFETY = "Safety"
    REASONING = "Reasoning"
    LOCALIZATION = "Localization"


class Severity(str, Enum):  # noqa: UP042 - preserve existing Enum string behavior
    """Issue severity levels used in evaluator notes."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DetectedIssue(BaseModel):
    """A single problem found during response review."""

    model_config = ConfigDict(extra="forbid")

    category: NonBlankStr
    severity: Severity
    description: NonBlankStr
    suggested_fix: NonBlankStr | None = None


class RubricScores(BaseModel):
    """1-5 rubric scores for a prompt-response comparison."""

    model_config = ConfigDict(extra="forbid")

    instruction_following: int = Field(ge=1, le=5)
    correctness: int = Field(ge=1, le=5)
    completeness: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    language_naturalness: int = Field(ge=1, le=5)
    formatting: int = Field(ge=1, le=5)
    safety: int = Field(ge=1, le=5)

    def average(self) -> float:
        """Return the arithmetic mean of all rubric dimensions."""

        values = (
            self.instruction_following,
            self.correctness,
            self.completeness,
            self.clarity,
            self.language_naturalness,
            self.formatting,
            self.safety,
        )
        return round(sum(values) / len(values), 2)


class PromptRecord(BaseModel):
    """A synthetic prompt used for evaluation practice."""

    model_config = ConfigDict(extra="forbid")

    id: NonBlankStr
    language: Language
    task_type: TaskType
    prompt: NonBlankStr
    expected_constraints: list[NonBlankStr] = Field(default_factory=list)


class ResponsePairRecord(BaseModel):
    """Two model responses for the same prompt."""

    model_config = ConfigDict(extra="forbid")

    id: NonBlankStr
    prompt_id: NonBlankStr
    response_a: NonBlankStr
    response_b: NonBlankStr
    model_a: NonBlankStr | None = None
    model_b: NonBlankStr | None = None


class EvaluationRecord(BaseModel):
    """A completed evaluator judgment for a response pair."""

    model_config = ConfigDict(extra="forbid")

    id: NonBlankStr
    prompt_id: NonBlankStr
    response_pair_id: NonBlankStr
    language: Language
    task_type: TaskType
    winner: Literal["A", "B", "Tie"]
    rubric_scores: RubricScores
    detected_issues: list[DetectedIssue] = Field(default_factory=list)
    rationale: NonBlankStr


SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "prompt": PromptRecord,
    "response": ResponsePairRecord,
    "evaluation": EvaluationRecord,
}
