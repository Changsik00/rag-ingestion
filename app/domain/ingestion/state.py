from datetime import datetime
from enum import Enum
from typing import Literal, TypedDict

from pydantic import BaseModel, Field

from app.domain.schemas.extraction import ExtractedMetadata


class StrategyType(str, Enum):
    """Backtracking Strategy Types"""
    STANDARD = "STANDARD"
    CORRECTION = "CORRECTION"  # Level 2: Reasoning Retry (Feedback-driven)
    RELAXATION = "RELAXATION"  # Level 3: Constraint Re-evaluation
    REINTERPRETATION = "REINTERPRETATION"  # Level 3: Ambiguity (Schema Switch)
    DECOMPOSITION = "DECOMPOSITION"  # Level 3: Chunking


class ValidationConstraints(BaseModel):
    """Validation Rules that can be relaxed"""
    strict_mode: bool = True
    max_retries: int = 3
    retry_depth: int = 0


class ValidationFeedback(BaseModel):
    """검증 단계에서 생성된 피드백 (System or User)"""
    source: Literal["validator", "user"]
    message: str
    target_fields: list[str] | None = None  # For Partial Retry
    timestamp: datetime = Field(default_factory=datetime.now)


class Attempt(BaseModel):
    """각 시도(Attempt)의 메타데이터 및 사고 과정 기록"""
    attempt_number: int
    strategy: StrategyType = StrategyType.STANDARD
    feedback: ValidationFeedback | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class IngestionState(TypedDict):
    """
    Ingestion Pipeline의 전체 상태를 관리하는 TypedDict.
    모든 Graph Node는 이 상태를 공유하고 필요한 필드를 업데이트합니다.
    """

    original_url: str
    raw_content: str
    metadata: ExtractedMetadata | None
    steps_history: list[str]

    # Reflexion & Logic Resolver State
    error: str | None
    retry_count: int
    max_retries: int

    # Polymorphic State
    current_strategy: StrategyType
    active_constraints: ValidationConstraints
    attempt_history: list[Attempt]
    last_feedback: ValidationFeedback | None
    predicted_category: str | None  # For Predictive Strategy

