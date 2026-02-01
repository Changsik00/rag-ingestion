from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.domain.value_objects.document_metadata import DocumentMetadata
from app.domain.value_objects.chunk import Chunk


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID를 str로 직렬화하여 사용 (Neo4j/Chroma 호환성)
    content: str
    metadata: DocumentMetadata
    chunks: list[Chunk] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = False
