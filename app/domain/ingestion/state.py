from typing import Any, TypedDict


class IngestionState(TypedDict):
    """
    Ingestion Pipeline의 전체 상태를 관리하는 TypedDict.
    모든 Graph Node는 이 상태를 공유하고 필요한 필드를 업데이트합니다.
    """

    original_url: str
    raw_content: str
    metadata: dict[str, Any]
    extracted_entities: list[dict[str, Any]]
    steps_history: list[str]  # 실행된 단계 기록 (debugging/audit)

    # Optional fields for error handling or branching
    error: str | None
    retry_count: int
