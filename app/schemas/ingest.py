from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class IngestRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target URL to ingest")


class IngestResponse(BaseModel):
    url: HttpUrl = Field(..., description="Source URL")
    markdown: str = Field(..., description="Extracted markdown content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extraction metadata")


class AsyncIngestResponse(BaseModel):
    job_id: str = Field(..., description="Unique Job ID to track progress")
    status: str = Field(..., description="Current status of the job (e.g. PENDING)")
