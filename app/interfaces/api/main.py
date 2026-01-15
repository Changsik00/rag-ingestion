from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, List
from uuid import UUID

from app.domain.models.ingest import IngestRequest, IngestResponse
from app.domain.entities.document import AtomicDocument
from app.domain.interfaces.document_repository import DocumentRepository
from app.infrastructure.scrapers.basic import BasicWebScraper
from app.infrastructure.storage.neo4j import Neo4jStorage
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.composite import CompositeStorage
from app.use_cases.ingestion import IngestionService

app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown and storing it in Atomic Layer",
    version="1.0.0"
)

# Dependency Injection
def get_scraper():
    return BasicWebScraper()

def get_repository() -> DocumentRepository:
    # In a real scenario, these might be singletons or managed by a DI container
    # For now, we instantiate them per request or use a global.
    # Using a simple composite for this MVP.
    neo4j = Neo4jStorage()
    chroma = ChromaStorage()
    return CompositeStorage(neo4j=neo4j, chroma=chroma)

def get_ingestion_service(
    scraper=Depends(get_scraper),
    repository=Depends(get_repository)
):
    return IngestionService(scraper=scraper, repository=repository)

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
