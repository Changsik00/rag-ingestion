from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated

from app.domain.models.ingest import IngestRequest, IngestResponse
from app.infrastructure.scrapers.basic import BasicWebScraper
from app.use_cases.ingestion import IngestionService

app = FastAPI(
    title="RAG Ingestion API",
    description="API for ingesting web content into Markdown",
    version="1.0.0"
)

# Dependency Injection
def get_scraper():
    return BasicWebScraper()

def get_ingestion_service(scraper=Depends(get_scraper)):
    return IngestionService(scraper=scraper)

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}
