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


class SessionTraceResponse(BaseResponse):
    messages: list[MessageDTO]
    values: dict[str, Any]
