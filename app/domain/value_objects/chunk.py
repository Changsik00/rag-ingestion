from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Chunk(BaseModel):
    """
    문서의 의미론적 분할 단위 (Semantic Unit).
    Value Object로 취급되어 불변성(frozen=True)을 가짐.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(description="청크의 고유 식별자 (UUID 등)")
    content: str = Field(description="청크 텍스트 내용")
    parent_id: str = Field(description="원본 Document ID")
    index: int = Field(description="문서 내 순서 (0-based)")
    embedding: list[float] | None = Field(default=None, description="Vector Embedding")
    metadata: dict[str, Any] = Field(default_factory=dict, description="청크 레벨 메타데이터")
