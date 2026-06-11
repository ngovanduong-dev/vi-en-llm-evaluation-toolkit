"""Core data models for synthetic LLM evaluation records."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Language(str, Enum):
    """Supported evaluation language modes."""

    VIETNAMESE = "Vietnamese"
    ENGLISH = "English"
    BILINGUAL = "Bilingual"


class TaskType(str, Enum):
    """Common task families for LLM evaluation work."""

    GENERAL = "General"
    TRANSLATION = "Translation"
    CODING = "Coding"
    SAFETY = "Safety"
    REASONING = "Reasoning"
    LOCALIZATION = "Localization"


class Severity(str, Enum):
    """Issue severity levels used in evaluator notes."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class DetectedIssue(BaseModel):
    """A single problem found during response review."""

    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1)
    severity: Severity
    description: str = Field(min_length=1)
    suggested_fix: str | None = None


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
        values = [
            self.instruction_following,
            self.correctness,
            self.completeness,
            self.clarity,
            self.language_naturalness,
            self.formatting,
            self.safety,
        ]
        return round(sum(values) / len(values), 2)


class PromptRecord(BaseModel):
    """A synthetic prompt used for evaluation practice."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    language: Language
    task_type: TaskType
    prompt: str = Field(min_length=1)
    expected_constraints: list[str] = Field(default_factory=list)

    @field_validator("expected_constraints")
    @classmethod
    def constraints_must_not_be_blank(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("expected_constraints cannot contain blank items")
        return values


class ResponsePairRecord(BaseModel):
    """Two model responses for the same prompt."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    prompt_id: str = Field(min_length=1)
    response_a: str = Field(min_length=1)
    response_b: str = Field(min_length=1)
    model_a: str | None = None
    model_b: str | None = None


class EvaluationRecord(BaseModel):
    """A completed evaluator judgment for a response pair."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    prompt_id: str = Field(min_length=1)
    response_pair_id: str = Field(min_length=1)
    language: Language
    task_type: TaskType
    winner: Literal["A", "B", "Tie"]
    rubric_scores: RubricScores
    detected_issues: list[DetectedIssue] = Field(default_factory=list)
    rationale: str = Field(min_length=1)

    @field_validator("rationale")
    @classmethod
    def rationale_must_contain_real_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rationale cannot be blank")
        return value


SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "prompt": PromptRecord,
    "response": ResponsePairRecord,
    "evaluation": EvaluationRecord,
}
