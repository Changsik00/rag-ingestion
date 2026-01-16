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
from app.use_cases.ingestion import IngestionService

@lru_cache
def get_neo4j_driver() -> Driver:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))

def get_scraper() -> ScraperInterface:
    return BasicWebScraper()

def get_repository() -> DocumentRepository:
    # Existing behavior: Neo4jStorage creates its own driver internally
    neo4j = Neo4jStorage()
    chroma = ChromaStorage()
    return CompositeStorage(neo4j=neo4j, chroma=chroma)

def get_job_repository() -> JobRepository:
    driver = get_neo4j_driver()
    return Neo4jJobRepository(driver=driver)

def get_ingestion_service(
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
    repository: Annotated[DocumentRepository, Depends(get_repository)],
    job_repository: Annotated[JobRepository, Depends(get_job_repository)]
) -> IngestionService:
    return IngestionService(scraper=scraper, repository=repository, job_repository=job_repository)
