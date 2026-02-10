from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.rag.orchestration.service import RAGOrchestrator
from app.domain.rag.brain.answer_generator import AnswerGenerator
from app.domain.rag.brain.reranker import Reranker
from app.domain.rag.brain.service import BrainService
from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import IntentType, UserIntent
from app.infrastructure.ai.rag_graph import RAGGraphBuilder
from app.infrastructure.rag.retrieval.service import RetrievalService


@pytest.fixture
def mock_brain():
    brain = MagicMock(spec=BrainService)
    # Async method needs to be explicitly set for AsyncMock when using spec
    brain.classify_and_rewrite = AsyncMock(
        return_value=(UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="test"), "rewritten")
    )
    return brain


@pytest.fixture
def mock_retrieval():
    retrieval = MagicMock(spec=RetrievalService)
    chunk = Chunk(id="1", content="content", parent_id="d1", index=0)
    retrieval.hybrid_search = AsyncMock(return_value=([chunk], [], []))
    return retrieval


@pytest.fixture
def mock_rerank_service():
    reranker = MagicMock(spec=Reranker)
    chunk = Chunk(id="1", content="content", parent_id="d1", index=0)
    reranker.rerank = AsyncMock(return_value=([chunk], []))
    return reranker


@pytest.fixture
def mock_generator():
    generator = MagicMock(spec=AnswerGenerator)
    generator.generate_answer = AsyncMock(return_value="Final Answer")
    generator.format_context.return_value = ("context", {})
    generator.parse_citations.return_value = []
    # Async methods on MagicMock need explicit setting sometimes
    # But generate_answer is async
    return generator


@pytest.fixture
def rag_service(mock_brain, mock_retrieval, mock_rerank_service, mock_generator):
    # Assemble 3-Layer Components
    orchestrator = RAGOrchestrator(
        brain_service=mock_brain,
        reranker=mock_rerank_service,
        answer_generator=mock_generator,
        retrieval_service=mock_retrieval,
    )

    # Build Graph
    builder = RAGGraphBuilder(orchestrator)
    graph = builder.build()

    # RAG service usually takes 'graph' argument in init if updated
    # Let's check RAG service definition
    return graph  # RAG service might wrap it, but graph is runnable


@pytest.mark.asyncio
async def test_rag_e2e_flow(rag_service, mock_brain, mock_retrieval):
    # Execute
    # Invoking graph directly
    initial_state = {"query": "test query", "history": [], "manual_filters": None, "reasoning_log": []}

    result = await rag_service.ainvoke(initial_state)

    # Verify
    assert result["final_answer"] == "Final Answer"

    # Verify Wiring
    mock_brain.classify_and_rewrite.assert_called_once()
    mock_retrieval.hybrid_search.assert_called_once()

    # Verify State Propagation
    assert result["rewritten_query"] == "rewritten"
    assert len(result["vector_chunks"]) == 1
