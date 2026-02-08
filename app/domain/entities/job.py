import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class IngestionJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_url: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: str | None = None
    retry_of: str | None = None
    raw_content: bytes | None = Field(default=None, exclude=True)  # For local file ingestion
    filename: str | None = None  # For local file ingestion
    docs_ids: list[str] = Field(default_factory=list)  # Associated document IDs
    chunking_config: dict | None = None  # Chunking configuration (strategy, size, etc.)

    # [Spec 065] Deduplication Fields
    content_hash: str | None = None
    custom_metadata: dict | None = None  # Flexible metadata for strategy-based deduplication
    skip_reason: str | None = None  # [Spec 072] Reason for skipping (if SKIPPED)

    model_config = ConfigDict(frozen=False)  # Allow updates
