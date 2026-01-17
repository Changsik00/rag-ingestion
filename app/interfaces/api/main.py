from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status

from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository
from app.interfaces.api.dependencies import get_ingestion_service, get_repository
from app.interfaces.api.endpoints.jobs import router as jobs_router
from app.schemas.ingest import AsyncIngestResponse, IngestRequest
from app.use_cases.ingestion import IngestionService

app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown and storing it in Atomic Layer",
    version="1.0.0"
)

app.include_router(jobs_router)

@app.post("/ingest/web", status_code=status.HTTP_202_ACCEPTED, response_model=AsyncIngestResponse)
async def ingest_web_page(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[IngestionService, Depends(get_ingestion_service)]
):
    try:
        job = service.create_job(str(request.url))
        background_tasks.add_task(service.process_job, job.job_id)
        return {"job_id": job.job_id, "status": job.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=list[AtomicDocument])
async def list_documents(
    repository: Annotated[DocumentRepository, Depends(get_repository)],
    limit: int = 10
):
    try:
        return repository.list_documents(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
