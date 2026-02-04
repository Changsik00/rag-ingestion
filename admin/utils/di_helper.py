
from psycopg_pool import AsyncConnectionPool

from app.application.services.rag import RAG
from app.core import database
from app.core.config import get_settings
from app.interfaces.api.dependencies import (
    get_checkpointer,
    get_chroma_vector_repository,
    get_intent_classifier,
    get_neo4j_driver,
    get_query_rewriter,
    get_rag_graph_builder,
    get_rag_nodes,
)


async def get_manual_rag_service() -> RAG:
    """Admin/Script 환경에서 RAG 서비스를 수동으로 생성"""
    settings = get_settings()

    # 1. Initialize Database Pool if not ready
    if not database.pool:
        database.pool = AsyncConnectionPool(
            conninfo=str(settings.POSTGRES_URL),
            open=False,
            kwargs={"autocommit": True}
        )
        await database.pool.open()

    # 2. Manual Dependency Injection
    driver = get_neo4j_driver()
    chroma_repo = get_chroma_vector_repository()
    query_rewriter = get_query_rewriter()
    intent_classifier = get_intent_classifier()

    # Assemble Nodes
    nodes = get_rag_nodes(driver, query_rewriter, intent_classifier, chroma_repo)

    # Assemble Builder
    builder = get_rag_graph_builder(nodes)

    # Get Checkpointer (Async Generator)
    checkpointer_gen = get_checkpointer()
    try:
        checkpointer = await anext(checkpointer_gen)
    except StopAsyncIteration:
        checkpointer = None

    # Build Service
    compiled_graph = builder.build(checkpointer=checkpointer)
    return RAG(graph=compiled_graph)
