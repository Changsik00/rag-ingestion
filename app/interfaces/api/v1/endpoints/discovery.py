from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.domain.services.discovery_service import DiscoveryService
from app.interfaces.api.dependencies import get_discovery_service
from app.interfaces.api.v1.dto.common import BaseResponse

router = APIRouter(prefix="/discovery", tags=["Discovery"])


class DiscoveryRequest(BaseModel):
    topic: str = Field(..., description="Topic to research")
    max_depth: int = Field(default=1, ge=0, le=3, description="Recursive crawling depth")
    max_docs: int = Field(default=10, ge=1, le=50, description="Maximum number of documents to ingest")


class DiscoveryResponse(BaseResponse):
    job_ids: list[str] = Field(..., description="List of started ingestion job IDs")
    message: str


@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=DiscoveryResponse)
async def start_discovery(
    request: DiscoveryRequest,
    service: Annotated[DiscoveryService, Depends(get_discovery_service)],
):
    """
    Start autonomous discovery for a topic.
    Searches Google, crawls recursively, and ingests useful content.
    """
    try:
        job_ids = await service.start_discovery(
            topic=request.topic, max_depth=request.max_depth, max_docs=request.max_docs
        )
        return DiscoveryResponse(
            job_ids=job_ids,
            message=f"Discovery started for '{request.topic}'. Triggered {len(job_ids)} ingestion jobs.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
