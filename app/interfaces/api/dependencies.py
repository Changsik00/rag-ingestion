from functools import lru_cache
from typing import Annotated
from fastapi import Depends
import os
from neo4j import GraphDatabase, Driver

from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.scraper import ScraperInterface
from app.domain.interfaces.job_repository import JobRepository

from app.infrastructure.scrapers.basic import BasicWebScraper
from app.infrastructure.storage.neo4j import Neo4jStorage
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.composite import CompositeStorage
from app.infrastructure.storage.neo4j_job_repo import Neo4jJobRepository
from app.domain.services.semantic_extractor import SemanticExtractor

@lru_cache
def get_semantic_extractor() -> SemanticExtractor:
    return SemanticExtractor()

def get_ingestion_service(
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
    repository: Annotated[DocumentRepository, Depends(get_repository)],
    job_repository: Annotated[JobRepository, Depends(get_job_repository)],
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)]
) -> IngestionService:
    return IngestionService(scraper=scraper, repository=repository, job_repository=job_repository, extractor=extractor)
