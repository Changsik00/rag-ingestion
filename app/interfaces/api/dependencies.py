import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from neo4j import Driver, GraphDatabase

from app.core.llm import get_llm
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.scraper import ScraperInterface
from app.domain.services.semantic_extractor import SemanticExtractor
from app.infrastructure.scrapers.basic import BasicWebScraper
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.composite import CompositeStorage
from app.infrastructure.storage.neo4j import Neo4jStorage
from app.infrastructure.storage.neo4j_graph import Neo4jGraphRepository
from app.infrastructure.storage.neo4j_job_repo import Neo4jJobRepository
from app.use_cases.ingestion import IngestionService


# Scraper dependency
@lru_cache
def get_scraper() -> ScraperInterface:
    return BasicWebScraper()


# Neo4j driver dependency
@lru_cache
def get_neo4j_driver() -> Driver:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))


# Document repository dependency
@lru_cache
def get_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> DocumentRepository:
    neo4j_storage = Neo4jStorage(driver)
    chroma_storage = ChromaStorage()
    return CompositeStorage(neo4j_storage, chroma_storage)


# Job repository dependency
@lru_cache
def get_job_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> JobRepository:
    return Neo4jJobRepository(driver)


# Semantic extractor dependency
@lru_cache
def get_semantic_extractor() -> SemanticExtractor:
    llm_adapter = get_llm()  # LangChainLLMAdapter 반환
    return SemanticExtractor(llm=llm_adapter)


# Graph repository dependency
@lru_cache
def get_graph_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> GraphRepository:
    return Neo4jGraphRepository(driver)


# Ingestion service dependency
def get_ingestion_service(
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
    repository: Annotated[DocumentRepository, Depends(get_repository)],
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    job_repository: Annotated[JobRepository, Depends(get_job_repository)],
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)]
) -> IngestionService:
    return IngestionService(
        scraper=scraper,
        repository=repository,
        graph=graph,
        job_repository=job_repository,
        extractor=extractor
    )
