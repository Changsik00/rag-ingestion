from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status

from app.application.interfaces.scraper import ScraperInterface
from app.application.services.ingestion import Ingestion
from app.interfaces.api.dependencies import get_ingestion_service, get_scraper
from app.interfaces.api.v1.dto.ingest import (
    AsyncIngestResponse,
    IngestRequest,
    IngestResponse,
    MultiAsyncIngestResponse,
)

router = APIRouter(prefix="/ingest", tags=["Ingest"])


@router.post("/web", status_code=status.HTTP_202_ACCEPTED, response_model=AsyncIngestResponse)
async def ingest_web_page(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[Ingestion, Depends(get_ingestion_service)],
):
    chunk_config_dict = request.chunking_config.model_dump() if request.chunking_config else None

    # [Spec 065] Pass force_refresh via custom_metadata
    custom_metadata = {"force_refresh": request.force_refresh}
    
    # Extract Video ID for YouTube if possible
    import re
    if "youtube.com" in str(request.url) or "youtu.be" in str(request.url):
        # Simple regex for video id
        # youtube.com/watch?v=VIDEO_ID
        # youtu.be/VIDEO_ID
        video_id = None
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", str(request.url))
        if match:
            video_id = match.group(1)
            custom_metadata["video_id"] = video_id

    # [Spec 065] Concurrency Check: Don't even create a job if one is already PENDING/RUNNING
    if not request.force_refresh:
        existing_job = service.is_already_queued(str(request.url))
        if existing_job:
            return AsyncIngestResponse(
                job_id=existing_job.job_id, 
                current_status=existing_job.status,
                message=f"Duplicate request. Job {existing_job.job_id} is already in state {existing_job.status}."
            )

    job = service.create_job(
        str(request.url),
        chunking_config=chunk_config_dict,
        custom_metadata=custom_metadata
    )
    background_tasks.add_task(service.process_job, job.job_id)
    return AsyncIngestResponse(
        job_id=job.job_id, 
        current_status=job.status,
        message="Ingestion job created successfully."
    )


@router.post("/files", status_code=status.HTTP_202_ACCEPTED, response_model=MultiAsyncIngestResponse)
async def ingest_files(
    background_tasks: BackgroundTasks,
    service: Annotated[Ingestion, Depends(get_ingestion_service)],
    files: list[UploadFile] = File(...),
):
    """
    Upload multiple local files (PDF, TXT, MD) for ingestion.
    """
    import hashlib
    job_responses = []
    for file in files:
        content = await file.read()
        
        # Calculate Metadata and Hash for Deduplication
        file_size = len(content)
        content_hash = hashlib.sha256(content).hexdigest()
        
        custom_metadata = {
            "file_size": file_size,
            "filename": file.filename
        }
        
        # source_url for file ingestion will be the filename for tracking
        # Ideally, should be careful about name collisions, but for now using filename
        job = service.create_job(
            url=f"file://{file.filename}", 
            raw_content=content, 
            filename=file.filename,
            custom_metadata=custom_metadata,
            # We can also pass content_hash directly if IngestionJob supports it, wait, create_job doesn't take content_hash arg in explicit signature?
            # Let's check ingestion.py signature. It has custom_metadata.
            # IngestionJob has content_hash field. We should update create_job to accept it or pass via metadata first?
            # Ideally create_job should accept content_hash.
        )
        # Manually set content_hash on job object before processing? 
        # Better: create_job signature update is preferred, but for now let's update job object or pass in metadata.
        # Check ingestion.py: create_job() takes (url, ..., custom_metadata). 
        # If I want to persist content_hash, I need to update create_job.
        # For now, let's put it in job object if service returns it.
        job.content_hash = content_hash
        service.job_repository.update_job(job) # Persist hash immediately
        
        background_tasks.add_task(service.process_job, job.job_id)
        job_responses.append(AsyncIngestResponse(job_id=job.job_id, current_status=job.status))

    return MultiAsyncIngestResponse(jobs=job_responses)


@router.post("/debug/scrape", response_model=IngestResponse)
async def debug_scrape(
    request: IngestRequest,
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
):
    """
    Directly scrapes a URL and returns the content without saving to DB.
    Useful for testing the scraper logic.
    """
    return await scraper.scrape(str(request.url))
