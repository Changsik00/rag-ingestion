from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from app.application.interfaces.scraper import ScraperInterface
from app.application.services.ingestion import Ingestion
from app.interfaces.api.dependencies import get_ingestion_service, get_scraper
from app.interfaces.api.dto.ingest import (
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
    try:
        job = service.create_job(str(request.url))
        background_tasks.add_task(service.process_job, job.job_id)
        return {"job_id": job.job_id, "status": job.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files", status_code=status.HTTP_202_ACCEPTED, response_model=MultiAsyncIngestResponse)
async def ingest_files(
    background_tasks: BackgroundTasks,
    service: Annotated[Ingestion, Depends(get_ingestion_service)],
    files: list[UploadFile] = File(...),
):
    """
    Upload multiple local files (PDF, TXT, MD) for ingestion.
    """
    job_responses = []
    try:
        for file in files:
            content = await file.read()
            # source_url for file ingestion will be the filename for tracking
            job = service.create_job(url=f"file://{file.filename}", raw_content=content, filename=file.filename)
            background_tasks.add_task(service.process_job, job.job_id)
            job_responses.append({"job_id": job.job_id, "status": job.status})

        return {"jobs": job_responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug/scrape", response_model=IngestResponse)
async def debug_scrape(
    request: IngestRequest,
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
):
    """
    Directly scrapes a URL and returns the content without saving to DB.
    Useful for testing the scraper logic.
    """
    try:
        return scraper.scrape(str(request.url))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
