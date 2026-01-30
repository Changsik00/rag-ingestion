import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IngestionJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_url: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: str | None = None
    retry_of: str | None = None
    raw_content: bytes | None = None  # For local file ingestion
    filename: str | None = None      # For local file ingestion
    docs_ids: list[str] = Field(default_factory=list)  # Associated document IDs

    class Config:
        frozen = False  # Allow updates
