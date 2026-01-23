from enum import Enum

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """사용자 의도 분류 타입"""

    GENERAL_QUERY = "general_query"  # 전체 지식 베이스 검색
    COMPARE = "compare"  # 특정 문서들 비교
    SUMMARIZE = "summarize"  # 특정 문서 요약
    FILTER_BY_TOPIC = "filter_by_topic"  # 주제/카테고리별 필터링


class UserIntent(BaseModel):
    """
    Intent Classifier의 출력 스키마.
    LLM이 반환하는 JSON을 구조화하고 검증한다.
    """

    intent: IntentType = Field(description="사용자 의도 분류 결과")
    targets: list[str] = Field(default_factory=list, description="검색 대상 (Document ID, URL, Entity Name 등)")
    reasoning: str = Field(description="의도 분류 근거 (디버깅용)")
