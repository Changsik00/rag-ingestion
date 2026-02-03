from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.interfaces.api.v1.dto.common import BaseResponse


class IngestRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target URL to ingest")
    chunking_config: dict | None = Field(default=None, description="Optional chunking configuration")


class IngestResponse(BaseResponse):
    """
    Response for debug scrape.
    """

    url: HttpUrl = Field(..., description="Source URL")
    markdown: str = Field(..., description="Extracted markdown content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extraction metadata")


class AsyncIngestResponse(BaseResponse):
    """
    Response for async ingestion job creation.
    """

    job_id: str = Field(..., description="Unique Job ID to track progress")
    current_status: str = Field(..., description="Current status of the job (e.g. PENDING)")


class MultiAsyncIngestResponse(BaseResponse):
    """
    Response for multiple async ingestion jobs (file upload).
    """

    jobs: list[AsyncIngestResponse] = Field(..., description="List of created jobs")
