from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile, status

from app.application.services.ingestion import Ingestion
from app.domain.entities.document import Document
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.scraper import ScraperInterface
from app.interfaces.api.dependencies import get_ingestion_service, get_repository, get_scraper
from app.interfaces.api.endpoints.entities import router as entities_router
from app.interfaces.api.endpoints.jobs import router as jobs_router
from app.interfaces.api.schemas.ingest import (
    AsyncIngestResponse,
    IngestRequest,
    IngestResponse,
    MultiAsyncIngestResponse,
)
from app.interfaces.api.v1.endpoints.admin import router as admin_router

app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown and storing it in Atomic Layer",
    version="1.0.0",
)

app.include_router(jobs_router)
app.include_router(entities_router)
app.include_router(admin_router, prefix="/api/v1/admin")


@app.post("/ingest/web", status_code=status.HTTP_202_ACCEPTED, response_model=AsyncIngestResponse)
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


@app.post("/ingest/files", status_code=status.HTTP_202_ACCEPTED, response_model=MultiAsyncIngestResponse)
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


@app.get("/documents", response_model=list[Document])
async def list_documents(repository: Annotated[DocumentRepository, Depends(get_repository)], limit: int = 10):
    try:
        return repository.list_documents(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/debug/scrape", response_model=IngestResponse)
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
