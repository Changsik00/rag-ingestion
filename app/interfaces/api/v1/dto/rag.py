from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.interfaces.api.v1.dto.common import BaseResponse


class DocumentDTO(BaseModel):
    """
    Data Transfer Object for Document entity.
    """

    id: str | None = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class RetrievalResponse(BaseResponse):
    """
    Response for retrieval operations.
    """

    query: str
    documents: list[DocumentDTO]
    count: int


class RAGResponse(BaseResponse):
    """
    Response for RAG generation.
    """

    query: str
    answer: str
    source_documents: list[DocumentDTO] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    content: str


class ChatResponse(BaseResponse):
    """
    Response for Conversational Agent.
    """

    current_status: str
    messages: list[MessageDTO]
    context_data: dict[str, Any] | None = None
    intent: str | None = None
    next: list[str] | tuple[str, ...] | None = None
    draft_content: str | None = None
    is_clarification: bool = False
    missing_slots: list[str] | None = None


class AutocompleteResponse(BaseModel):
    id: str
    title: str


class AdvancedSettings(BaseModel):
    """
    Advanced settings for RAG pipeline tuning.
    """

    top_k: int = Field(default=5, ge=1, le=100, description="검색할 문서의 개수")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0, description="LLM 생성 온도")
    search_strategy: str = Field(
        default="hybrid",
        pattern="^(hybrid|vector|keyword)$",
        description="검색 전략 (hybrid, vector, keyword)",
    )


class ChatRequest(BaseModel):
    """
    Request DTO for Chat Agent.
    """

    message: str = Field(..., min_length=1, description="사용자 질문 메시지")
    filters: dict[str, Any] = Field(default_factory=dict, description="메타데이터 필터")
    hitl_enabled: bool = Field(default=False, description="Human-in-the-Loop 활성화 여부")
    advanced_settings: AdvancedSettings = Field(default_factory=AdvancedSettings, description="고급 검색 설정")


class SessionTraceResponse(BaseResponse):
    messages: list[MessageDTO]
    values: dict[str, Any]
