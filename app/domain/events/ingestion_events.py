from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseIngestionEvent(BaseModel):
    job_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(frozen=True)

class IngestionStarted(BaseIngestionEvent):
    source_url: str

class ContentCollected(BaseIngestionEvent):
    raw_content: str | bytes
    metadata: dict[str, Any] = Field(default_factory=dict)

class ContentUnique(BaseIngestionEvent):
    content_hash: str
    raw_content: str | bytes
    metadata: dict[str, Any] = Field(default_factory=dict)

class MetadataExtracted(BaseIngestionEvent):
    extracted_metadata: dict[str, Any]
    raw_content: str | bytes | None = None

class DocumentChunked(BaseIngestionEvent):
    chunks: list[dict[str, Any]]
    semantic_data: dict[str, Any] | None = None

class ChunksEmbedded(BaseIngestionEvent):
    # This might include a list of chunks with their vectors
    pass

class DataIndexed(BaseIngestionEvent):
    doc_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class IngestionFailed(BaseIngestionEvent):
    stage: str
    error_message: str
    exc_info: str | None = None

class IngestionCompleted(BaseIngestionEvent):
    doc_id: str
