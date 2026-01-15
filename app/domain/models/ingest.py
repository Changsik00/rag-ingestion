from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any

class IngestRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target URL to ingest")

class IngestResponse(BaseModel):
    url: HttpUrl = Field(..., description="Source URL")
    markdown: str = Field(..., description="Extracted markdown content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extraction metadata")
