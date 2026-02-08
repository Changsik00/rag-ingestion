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

    # [Spec 065] Extract Metadata for deduplication check
    custom_metadata = {"force_refresh": request.force_refresh}
    import re

    if "youtube.com" in str(request.url) or "youtu.be" in str(request.url):
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", str(request.url))
        if match:
            custom_metadata["video_id"] = match.group(1)

    # [Spec 072] Removed early deduplication to allow SKIPPED status creation
    # All deduplication logic is now handled in process_job() for proper status tracking
    job = service.create_job(str(request.url), chunking_config=chunk_config_dict, custom_metadata=custom_metadata)
    background_tasks.add_task(service.process_job, job.job_id, request.force_refresh)
    return AsyncIngestResponse(
        job_id=job.job_id, current_status=job.status, message="Ingestion job created successfully."
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
        file_size = len(content)
        content_hash = hashlib.sha256(content).hexdigest()

        # [Spec 065] Early Deduplication Check for Files
        existing_job = service.is_already_queued(url=f"file://{file.filename}", content_hash=content_hash)
        if existing_job:
            job_responses.append(
                AsyncIngestResponse(
                    job_id=existing_job.job_id,
                    current_status=existing_job.status,
                    message=f"File '{file.filename}' already processed (Job {existing_job.job_id}).",
                )
            )
            continue

        custom_metadata = {"file_size": file_size, "filename": file.filename}

        job = service.create_job(
            url=f"file://{file.filename}",
            raw_content=content,
            filename=file.filename,
            custom_metadata=custom_metadata,
            content_hash=content_hash,
        )

        background_tasks.add_task(service.process_job, job.job_id)
        job_responses.append(
            AsyncIngestResponse(
                job_id=job.job_id, current_status=job.status, message=f"File '{file.filename}' ingestion started."
            )
        )

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
