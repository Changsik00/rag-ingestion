from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from neo4j import Driver, GraphDatabase

from app.application.services.admin_agent import AdminAgent
from app.application.services.ingestion import IngestionUseCase
from app.application.services.integrity import Integrity
from app.application.services.rag import RAG
from app.application.services.semantic_extractor import SemanticExtractor
from app.core.config import get_settings
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.scraper import ScraperInterface
from app.domain.interfaces.chunker import Chunker
from app.domain.services.feedback import Feedback
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter
from app.infrastructure.brain.adapter import LangGraphAdapter
from app.infrastructure.chunker.langchain_chunker import LangChainChunker
from app.infrastructure.factories.llm_factory import LLMFactory
from app.infrastructure.scrapers.composite_scraper import CompositeScraper
from app.infrastructure.storage.chroma import ChromaVectorRepository
from app.infrastructure.storage.composite import CompositeDocumentRepository
from app.infrastructure.storage.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository

# === Dependency Injection 컨테이너 ===
# FastAPI의 Depends를 사용하여 각 레이어의 구현체를 주입합니다.
# 모든 의존성은 함수로 정의되어 테스트 시 Mock으로 대체 가능합니다.


# Scraper 의존성 (웹 페이지 스크래핑)
@lru_cache
def get_scraper() -> ScraperInterface:
    return CompositeScraper()


# Neo4j Driver 의존성 (모든 Neo4j 저장소가 공유하는 단일 Driver)
@lru_cache
def get_neo4j_driver() -> Driver:
    settings = get_settings()
    return GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))


# Document Repository 의존성 (CompositeStorage: Neo4j + ChromaDB)
@lru_cache
def get_chroma_vector_repository() -> ChromaVectorRepository:
    return ChromaVectorRepository()


@lru_cache
def get_repository() -> DocumentRepository:
    """Composite Storage를 DI로 제공"""
    driver = get_neo4j_driver()
    neo4j_storage = Neo4jDocumentRepository(driver)
    chroma_storage = get_chroma_vector_repository() # Use the dependency function

    return CompositeDocumentRepository([neo4j_storage, chroma_storage])


# Job Repository 의존성 (IngestionJob 관리)
@lru_cache
def get_job_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> JobRepository:
    return Neo4jJobRepository(driver)


# Storage Integrity Service 의존성
# Deleted get_storage_integrity_service



# Checkpointer 의존성 (HITL Persistence)
_checkpointer_instance: AsyncSqliteSaver | None = None
_checkpointer_conn: Any = None
_creation_loop: Any = None


async def get_checkpointer() -> AsyncSqliteSaver:
    global _checkpointer_instance, _checkpointer_conn, _creation_loop
    import asyncio

    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _checkpointer_instance is None or (current_loop and _creation_loop != current_loop):
        import aiosqlite

        # 이전 연결이 있고 루프가 바뀌었다면 닫기 시도 (Best effort)
        if _checkpointer_conn and _creation_loop != current_loop:
            try:
                # 주의: 다른 루프의 연결을 현재 루프에서 닫는 것이 실패할 수 있음
                pass
            except Exception:
                pass

        # 싱글톤 연결 생성 (루프별)
        _checkpointer_conn = await aiosqlite.connect("checkpoints.sqlite")
        # WAL 모드 활성화로 멀티 프로세스 동시성 향상
        await _checkpointer_conn.execute("PRAGMA journal_mode=WAL;")
        _checkpointer_instance = AsyncSqliteSaver(_checkpointer_conn)
        # 테이블 생성 등 초기화 작업 수행
        await _checkpointer_instance.setup()
        _creation_loop = current_loop

    return _checkpointer_instance


# Semantic Extractor 의존성 (LLM 기반 메타데이터 추출)
async def get_semantic_extractor(
    checkpointer: Annotated[AsyncSqliteSaver, Depends(get_checkpointer)],
) -> SemanticExtractor:
    llm_adapter = LLMFactory.get_llm_adapter()  # LangChainLLMAdapter를 반환
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
def get_chunker() -> Chunker:
    return LangChainChunker()


# Ingestion Service 의존성 (전체 수집 워크플로우)
def get_ingestion_service(
    scraper: Annotated[ScraperInterface, Depends(get_scraper)],
    repository: Annotated[DocumentRepository, Depends(get_repository)],
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    job_repository: Annotated[JobRepository, Depends(get_job_repository)],
    chunker: Annotated[Chunker, Depends(get_chunker)],
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)],
) -> IngestionUseCase:
    return IngestionUseCase(
        scraper=scraper,
        repository=repository,
        graph=graph,
        job_repository=job_repository,
        chunker=chunker,
        extractor=extractor,
    )


# Spec 024: LangGraphAdapter 직접 접근 (HITL Control용)
async def get_langgraph_adapter(
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)],
) -> LangGraphAdapter:
    # SemanticExtractor.llm is the LangGraphAdapter
    if isinstance(extractor.llm, LangGraphAdapter):
        return extractor.llm
    raise ValueError("SemanticExtractor is not using LangGraphAdapter")


# === RAG Service Dependencies (Spec 032) ===


# Query Rewriter 의존성
@lru_cache
def get_query_rewriter() -> QueryRewriter:
    llm_adapter = LLMFactory.get_llm_adapter()
    return QueryRewriter(llm_adapter)


# Intent Classifier 의존성 (Spec 032)
@lru_cache
def get_intent_classifier() -> IntentClassifier:
    llm_adapter = LLMFactory.get_llm_adapter()
    return IntentClassifier(llm_adapter)


# RAG Nodes 의존성 (Spec 033)
def get_rag_nodes(
    driver: Annotated[Driver, Depends(get_neo4j_driver)],
    query_rewriter: Annotated[QueryRewriter, Depends(get_query_rewriter)],
    intent_classifier: Annotated[IntentClassifier, Depends(get_intent_classifier)],
    chroma_repo: Annotated[ChromaVectorRepository, Depends(get_chroma_vector_repository)],
):
    from app.infrastructure.rag.nodes import RAGNodes

    neo4j_doc_repo = Neo4jDocumentRepository(driver)
    neo4j_graph_repo = Neo4jGraphRepository(driver)
    llm_adapter = LLMFactory.get_llm_adapter()

    return RAGNodes(
        neo4j_doc_repo=neo4j_doc_repo,
        neo4j_graph_repo=neo4j_graph_repo,
        chroma_repo=chroma_repo,
        query_rewriter=query_rewriter,
        intent_classifier=intent_classifier,
        llm=llm_adapter,
    )


# RAG Graph Builder 의존성 (Spec 033)
def get_rag_graph_builder(nodes=Depends(get_rag_nodes)):
    from app.infrastructure.rag.graph import RAGGraphBuilder

    return RAGGraphBuilder(nodes)


# RAG Service 의존성 (Spec 033: LangGraph 기반)
async def get_rag_service(
    graph_builder=Depends(get_rag_graph_builder),
    checkpointer: Annotated[AsyncSqliteSaver, Depends(get_checkpointer)] = None,
) -> RAG:
    # Build Graph with Checkpointer
    compiled_graph = graph_builder.build(checkpointer=checkpointer)

    return RAG(graph=compiled_graph)


# Admin Agent 의존성 (Spec 038)
async def get_admin_agent(
    rag_service: Annotated[RAG, Depends(get_rag_service)],
    ingestion_service: Annotated[IngestionUseCase, Depends(get_ingestion_service)],
) -> AdminAgent:
    return AdminAgent(rag_service=rag_service, ingestion_service=ingestion_service)


# Feedback Service 의존성
@lru_cache
def get_feedback_service() -> Feedback:
    return Feedback()


# Integrity Service 의존성 (Spec 042)
async def get_integrity_service(
    driver: Annotated[Driver, Depends(get_neo4j_driver)],
    checkpointer: Annotated[AsyncSqliteSaver, Depends(get_checkpointer)],
    chroma_storage: Annotated[ChromaVectorRepository, Depends(get_chroma_vector_repository)],
) -> Integrity:
    from app.application.services.integrity import Integrity

    neo4j_storage = Neo4jDocumentRepository(driver)
    # 어댑터 생성 (Checkpointer 리셋용)
    llm_adapter = LLMFactory.get_llm_adapter()
    langgraph_adapter = LangGraphAdapter(llm=llm_adapter, checkpointer=checkpointer)

    return Integrity(
        primary_repo=neo4j_storage,
        target_repo=chroma_storage,
        langgraph_adapter=langgraph_adapter,
    )
