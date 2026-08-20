"""Domain models for pairwise technical-response evaluations."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from vi_en_eval.schemas import NonBlankStr, Severity


class TechnicalIssueCategory(str, Enum):  # noqa: UP042 - match shared Enum behavior
    """General categories for issues found in technical responses."""

    CORRECTNESS_LOGIC = "Correctness/Logic"
    EDGE_CASE = "Edge Case"
    EFFICIENCY = "Efficiency"
    API_CONTRACT = "API/Contract"
    SECURITY_RELIABILITY = "Security/Reliability"
    CONCURRENCY = "Concurrency"
    EXPLANATION = "Explanation"
    STRUCTURED_OUTPUT = "Structured Output"


class TechnicalIssue(BaseModel):
    """A single problem detected in one technical-response candidate."""

    model_config = ConfigDict(extra="forbid")

    category: TechnicalIssueCategory
    severity: Severity
    description: NonBlankStr
    suggested_fix: NonBlankStr | None = None


class TechnicalRubricScores(BaseModel):
    """Per-candidate scores for the technical-response rubric."""

    model_config = ConfigDict(extra="forbid")

    instruction_following: int = Field(ge=1, le=5)
    correctness: int = Field(ge=1, le=5)
    edge_case_handling: int = Field(ge=1, le=5)
    efficiency: int = Field(ge=1, le=5)
    maintainability: int = Field(ge=1, le=5)
    security_reliability: int = Field(ge=1, le=5)
    explanation_quality: int = Field(ge=1, le=5)


class CandidateTechnicalAssessment(BaseModel):
    """Rubric scores and findings for one technical-response candidate."""

    model_config = ConfigDict(extra="forbid")

    rubric_scores: TechnicalRubricScores
    detected_issues: list[TechnicalIssue] = Field(default_factory=list)
    rationale: NonBlankStr


TechnicalWinner: TypeAlias = Literal["A", "B", "Tie"]
EvaluatorConfidence: TypeAlias = Annotated[float, Field(strict=True, ge=0.0, le=1.0)]


class PairwiseTechnicalEvaluation(BaseModel):
    """An independent assessment of both candidates in a response pair."""

    model_config = ConfigDict(extra="forbid")

    id: NonBlankStr
    prompt_id: NonBlankStr
    response_pair_id: NonBlankStr
    candidate_a: CandidateTechnicalAssessment
    candidate_b: CandidateTechnicalAssessment
    winner: TechnicalWinner
    confidence: EvaluatorConfidence
    rationale: NonBlankStr
