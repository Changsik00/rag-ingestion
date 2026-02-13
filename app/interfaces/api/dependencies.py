from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from neo4j import Driver, GraphDatabase

from app.application.interfaces.scraper import ScraperInterface
from app.application.services.agent import ConversationalRAGAgent
from app.application.services.feedback import Feedback
from app.application.services.ingestion import Ingestion
from app.application.services.integrity import Integrity
from app.application.saga.ingestion_handlers import IngestionSagaHandlers
from app.application.services.orchestration.chat import ChatOrchestrator
from app.application.services.orchestration.ingest import IngestOrchestrator
from app.application.services.rag import RAG
from app.application.services.semantic_extractor import SemanticExtractor
from app.core import database
from app.core.config import get_settings
from app.domain.interfaces.brain import IAnswerGenerator, IBrainService, IReranker
from app.domain.interfaces.chunker import Chunker
from app.domain.interfaces.document_repository import DocumentRepository
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.interfaces.job_repository import JobRepository
from app.domain.interfaces.retrieval import IRetrievalService
from app.domain.services.filter_matcher import FilterMatcher
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter
from app.infrastructure.ai.ingest.graph_builder import IngestionGraphBuilder
from app.infrastructure.chunker.langchain_chunker import LangChainChunker
from app.infrastructure.factories.llm_factory import LLMFactory
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.composite import CompositeDocumentRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.repositories.neo4j_job_repository import Neo4jJobRepository
from app.infrastructure.scrapers.composite_scraper import CompositeScraper

# === Dependency Injection 컨테이너 ===
# FastAPI의 Depends를 사용하여 각 레이어의 구현체를 주입합니다.
# 모든 의존성은 함수로 정의되어 테스트 시 Mock으로 대체 가능합니다.


# Scraper 의존성 (웹 페이지 스크래핑)
@lru_cache
def get_scraper() -> ScraperInterface:
    return CompositeScraper()


# Google Search Client 의존성 (Spec 078)
@lru_cache
def get_google_search_client() -> "GoogleSearchClient":
    from app.infrastructure.external_api.google_search_client import GoogleSearchClient

    settings = get_settings()
    if not settings.GOOGLE_API_KEY or not settings.GOOGLE_CSE_ID:
        # Optional: Warn or raise based on strictness. 
        # For now, we assume it's configured if this dependency is requested.
        pass
        
    return GoogleSearchClient(
        api_key=settings.GOOGLE_API_KEY or "", 
        cse_id=settings.GOOGLE_CSE_ID or ""
    )


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
    chroma_storage = get_chroma_vector_repository()  # Use the dependency function

    return CompositeDocumentRepository(neo4j=neo4j_storage, chroma=chroma_storage)


# Job Repository 의존성 (IngestionJob 관리)
@lru_cache
def get_job_repository(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> JobRepository:
    return Neo4jJobRepository(driver)


# Storage Integrity Service 의존성
# Deleted get_storage_integrity_service


# Checkpointer 의존성 (LangGraph State Persistence) - Spec 060: Postgres
async def get_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    if not database.pool:
        # DB Pool이 초기화되지 않은 경우 (예: 테스트 등) 실패
        raise RuntimeError("Database pool has not been initialized. Check lifespan handler.")

    async with database.pool.connection() as conn:
        checkpointer = AsyncPostgresSaver(conn)
        # setup()은 lifespan에서 수행하므로 생략 가능, 혹은 안전을 위해 다시 호출 (idempotent)
        # 여기서는 바로 반환
        yield checkpointer


# Semantic Extractor 의존성 (LLM 기반 메타데이터 추출)
async def get_semantic_extractor(
    checkpointer: Annotated[AsyncPostgresSaver, Depends(get_checkpointer)],
) -> SemanticExtractor:
    llm_adapter = LLMFactory.get_llm_adapter()

    # Brain interfaces/implementations are shared
    graph_builder = IngestionGraphBuilder(llm=llm_adapter)
    orchestrator = IngestOrchestrator(graph_builder=graph_builder)
    # Checkpointer might need to be passed to graph_builder or orchestrator if used inside
    return SemanticExtractor(llm=orchestrator)


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
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)],
    chunker: Annotated[Chunker, Depends(get_chunker)],
) -> Ingestion:
    # [Spec 076] Register Saga Handlers using the singleton-like initialize method
    IngestionSagaHandlers.initialize(
        job_repository=job_repository,
        document_repository=repository,
        graph_repository=graph,
        scraper=scraper,
        extractor=extractor,
        chunker=chunker
    )

    return Ingestion(
        scraper=scraper,
        repository=repository,
        graph=graph,
        job_repository=job_repository,
        extractor=extractor,
        chunker=chunker
    )


# Spec 024: IngestOrchestrator 직접 접근 (HITL Control용)
async def get_ingest_orchestrator(
    extractor: Annotated[SemanticExtractor, Depends(get_semantic_extractor)],
) -> IngestOrchestrator:
    # SemanticExtractor.llm is the IngestOrchestrator
    if isinstance(extractor.llm, IngestOrchestrator):
        return extractor.llm
    raise ValueError("SemanticExtractor is not using IngestOrchestrator")


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


# FilterMatcher 의존성 (Spec 073: Fuzzy Filter Matching)
@lru_cache
def get_filter_matcher(
    chroma_repo: Annotated[ChromaVectorRepository, Depends(get_chroma_vector_repository)],
) -> "FilterMatcher":
    # ChromaDB의 Embedding 함수를 재사용
    # LangChain의 embed_query를 사용 (단일 쿼리 임베딩)
    embedding_fn = chroma_repo.embedding_function

    # Wrapper to convert from batch function to single query function
    def single_query_embed(text: str) -> list[float]:
        # ChromaDB embedding_function expects list, returns list[list[float]]
        result = embedding_fn([text])
        return result[0] if result else []

    return FilterMatcher(embedding_fn=single_query_embed, similarity_threshold=0.85)


# === Refined 3-Layer Dependencies (Spec 076) ===


@lru_cache
def get_brain_service(
    intent_classifier: Annotated[IntentClassifier, Depends(get_intent_classifier)],
    query_rewriter: Annotated[QueryRewriter, Depends(get_query_rewriter)],
) -> "IBrainService":
    from app.infrastructure.brain.service import BrainService

    return BrainService(intent_classifier, query_rewriter)


@lru_cache
def get_retrieval_service(
    driver: Annotated[Driver, Depends(get_neo4j_driver)],
    chroma_repo: Annotated[ChromaVectorRepository, Depends(get_chroma_vector_repository)],
) -> "IRetrievalService":
    from app.infrastructure.retrieval.service import RetrievalService

    neo4j_doc_repo = Neo4jDocumentRepository(driver)
    neo4j_graph_repo = Neo4jGraphRepository(driver)
    return RetrievalService(neo4j_doc_repo, neo4j_graph_repo, chroma_repo)


@lru_cache
def get_reranker(driver: Annotated[Driver, Depends(get_neo4j_driver)]) -> "IReranker":
    from app.infrastructure.brain.reranker import Reranker

    llm = LLMFactory.get_llm_adapter()
    neo4j_doc_repo = Neo4jDocumentRepository(driver)
    return Reranker(llm, neo4j_doc_repo)


@lru_cache
def get_answer_generator() -> "IAnswerGenerator":
    from app.infrastructure.brain.answer_generator import AnswerGenerator

    llm = LLMFactory.get_llm_adapter()
    return AnswerGenerator(llm)


def get_chat_orchestrator(
    brain_service: Annotated["IBrainService", Depends(get_brain_service)],
    reranker: Annotated["IReranker", Depends(get_reranker)],
    answer_generator: Annotated["IAnswerGenerator", Depends(get_answer_generator)],
    retrieval_service: Annotated["IRetrievalService", Depends(get_retrieval_service)],
    filter_matcher: Annotated["FilterMatcher", Depends(get_filter_matcher)],
) -> ChatOrchestrator:
    return ChatOrchestrator(
        brain_service=brain_service,
        reranker=reranker,
        answer_generator=answer_generator,
        retrieval_service=retrieval_service,
        filter_matcher=filter_matcher,
    )


# RAG Graph Builder 의존성 (Updated for Spec 076)
def get_rag_graph_builder(orchestrator: Annotated[ChatOrchestrator, Depends(get_chat_orchestrator)]):
    from app.infrastructure.ai.chat.graph_builder import ChatGraphBuilder

    return ChatGraphBuilder(orchestrator)


# RAG Service 의존성 (Spec 033: LangGraph 기반)
async def get_rag_service(
    graph_builder=Depends(get_rag_graph_builder),
    checkpointer: Annotated[AsyncPostgresSaver, Depends(get_checkpointer)] = None,
) -> RAG:
    # Build Graph with Checkpointer
    compiled_graph = graph_builder.build(checkpointer=checkpointer)

    return RAG(graph=compiled_graph)


# Admin Agent 의존성 (Spec 038)
async def get_conversational_rag_agent(
    rag_service: Annotated[RAG, Depends(get_rag_service)],
    ingestion_service: Annotated[Ingestion, Depends(get_ingestion_service)],
) -> ConversationalRAGAgent:
    return ConversationalRAGAgent(rag_service=rag_service, ingestion_service=ingestion_service)


# Feedback Service 의존성
@lru_cache
def get_feedback_service() -> Feedback:
    return Feedback()

    # Integrity Service 의존성 (Spec 042)


async def get_integrity_service(
    driver: Annotated[Driver, Depends(get_neo4j_driver)],
    checkpointer: Annotated[AsyncPostgresSaver, Depends(get_checkpointer)],
    chroma_storage: Annotated[ChromaVectorRepository, Depends(get_chroma_vector_repository)],
) -> Integrity:
    from app.application.services.integrity import Integrity
    from app.infrastructure.ai.ingest.graph_builder import IngestionGraphBuilder

    neo4j_storage = Neo4jDocumentRepository(driver)
    llm_adapter = LLMFactory.get_llm_adapter()

    graph_builder = IngestionGraphBuilder(llm=llm_adapter)
    orchestrator = IngestOrchestrator(graph_builder=graph_builder)

    return Integrity(
        primary_repo=neo4j_storage,
        target_repo=chroma_storage,
        langgraph_adapter=orchestrator,
    )


# Session Repository 의존성 (Spec 062)
def get_session_repository():
    from app.infrastructure.repositories.postgres_session_repository import PostgresSessionRepository

    if not database.pool:
        raise RuntimeError("Database pool has not been initialized.")

    return PostgresSessionRepository(database.pool)
