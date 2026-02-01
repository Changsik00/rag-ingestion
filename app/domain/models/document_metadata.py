from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentMetadata(BaseModel):
    """
    문서의 메타데이터를 표현하는 Value Object.
    단순 Dict 대신 사용하여 Type Safety와 Validation을 보장함.
    """

    model_config = ConfigDict(frozen=True, extra="allow")  # 추가 필드 허용

    source_id: str = Field(..., description="원본 소스의 고유 식별자 (URL or File Path)")
    title: str | None = Field(None, description="문서 제목")
    author: str | None = Field(None, description="작성자")
    url: str | None = Field(None, description="원본 URL")
    created_at: datetime | None = Field(None, description="생성 일시")
    category: str | None = Field(None, description="카테고리")

    # 딕셔너리 호환성을 위한 헬퍼 (Pydantic 모델은 dict() 메서드 제공)
