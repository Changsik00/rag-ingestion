from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from neo4j import Driver, GraphDatabase

from app.core.config import get_settings
from app.core.llm import get_llm
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.scraper import ScraperInterface
from app.domain.services.chunker import ChunkerService
from app.domain.services.semantic_extractor import SemanticExtractor
from app.infrastructure.brain.adapter import LangGraphAdapter
from app.infrastructure.chunker.langchain_chunker import LangChainChunker
from app.infrastructure.scrapers.basic import BasicWebScraper
from app.infrastructure.storage.chroma import ChromaStorage
from app.infrastructure.storage.composite import CompositeStorage
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
from app.use_cases.ingestion import IngestionService

# === Dependency Injection 컨테이너 ===
# FastAPI의 Depends를 사용하여 각 레이어의 구현체를 주입합니다.
# 모든 의존성은 함수로 정의되어 테스트 시 Mock으로 대체 가능합니다.


# Scraper 의존성 (웹 페이지 스크래핑)
@lru_cache
def get_scraper() -> ScraperInterface:
    return BasicWebScraper()


# Neo4j Driver 의존성 (모든 Neo4j 저장소가 공유하는 단일 Driver)
@lru_cache
def get_neo4j_driver() -> Driver:
    settings = get_settings()
    return GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))


# Document Repository 의존성 (CompositeStorage: Neo4j + ChromaDB)
@lru_cache
def get_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> DocumentRepository:
    neo4j_storage = Neo4jStorage(driver)
    chroma_storage = ChromaStorage()
    return CompositeStorage(neo4j_storage, chroma_storage)


# Job Repository 의존성 (IngestionJob 관리)
@lru_cache
def get_job_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> JobRepository:
    return Neo4jJobRepository(driver)


# Semantic Extractor 의존성 (LLM 기반 메타데이터 추출)
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Checkpointer 의존성 (HITL Persistence)
@lru_cache
def get_checkpointer() -> SqliteSaver:
    # Use check_same_thread=False for FastAPI/Streamlit concurrency
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    return SqliteSaver(conn)

# Semantic Extractor 의존성 (LLM 기반 메타데이터 추출)
@lru_cache
def get_semantic_extractor(checkpointer: Annotated[SqliteSaver, Depends(get_checkpointer)]) -> SemanticExtractor:
    llm_adapter = get_llm()  # LangChainLLMAdapter를 반환
    # Spec 020: LangGraphAdapter를 통해 그래프 기반 추출 실행
    # Spec 024: Checkpointer 주입
    langgraph_adapter = LangGraphAdapter(llm=llm_adapter, checkpointer=checkpointer)
    return SemanticExtractor(llm=langgraph_adapter)


# Graph Repository 의존성 (Entity 및 관계 저장)
@lru_cache
def get_graph_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> GraphRepository:
    return Neo4jGraphRepository(driver)


# Chunker Service 의존성 (Spec 019: LangChain RecursiveCharacterTextSplitter)
@lru_cache
def get_chunker() -> ChunkerService:
    return LangChainChunker()


# Ingestion Service 의존성 (전체 수집 워크플로우)
def get_ingestion_service(
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
    repository: Annotated[DocumentRepository, Depends(get_repository)],
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    job_repository: Annotated[JobRepository, Depends(get_job_repository)],
    chunker: Annotated[ChunkerService, Depends(get_chunker)],
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)],
) -> IngestionService:
    return IngestionService(
        scraper=scraper,
        repository=repository,
        graph=graph,
        job_repository=job_repository,
        chunker=chunker,
        extractor=extractor,
    )

# Spec 024: LangGraphAdapter 직접 접근 (HITL Control용)
def get_langgraph_adapter(
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)]
) -> LangGraphAdapter:
    # SemanticExtractor.llm is the LangGraphAdapter
    if isinstance(extractor.llm, LangGraphAdapter):
        return extractor.llm
    raise ValueError("SemanticExtractor is not using LangGraphAdapter")
