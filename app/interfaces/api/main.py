from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, List

from app.schemas.ingest import IngestRequest, IngestResponse
from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository
from app.use_cases.ingestion import IngestionService

from app.interfaces.api.dependencies import get_ingestion_service, get_repository
from app.interfaces.api.endpoints.jobs import router as jobs_router

app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown and storing it in Atomic Layer",
    version="1.0.0"
)

app.include_router(jobs_router)

@app.post("/ingest/web", response_model=IngestResponse)
async def ingest_web_page(
    request: IngestRequest,
    service: Annotated[IngestionService, Depends(get_ingestion_service)]
):
    try:
        result = service.ingest(str(request.url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[AtomicDocument])
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
