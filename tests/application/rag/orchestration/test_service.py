from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.rag.orchestration.service import RAGOrchestrator
from app.domain.rag.brain.answer_generator import AnswerGenerator
from app.domain.rag.brain.reranker import Reranker
from app.domain.rag.brain.service import BrainService
from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import IntentType, UserIntent
from app.infrastructure.rag.retrieval.service import RetrievalService


@pytest.fixture
def mock_components():
    brain = AsyncMock(spec=BrainService)
    reranker = AsyncMock(spec=Reranker)
    # generator needs to mock both async and sync methods
    generator = MagicMock(spec=AnswerGenerator)
    generator.generate_answer = AsyncMock() # Explicitly mock async method
    retrieval = AsyncMock(spec=RetrievalService)
    return brain, reranker, generator, retrieval

@pytest.fixture
def orchestrator(mock_components):
    brain, reranker, generator, retrieval = mock_components
    # Mock synchronous method return values
    generator.format_context.return_value = ("context", {})
    generator.parse_citations.return_value = []
    # Mock async method return values
    generator.generate_answer.return_value = "Final Answer"

    return RAGOrchestrator(brain, reranker, generator, retrieval)

@pytest.mark.asyncio
async def test_run_pipeline(orchestrator, mock_components):
    brain, reranker, generator, retrieval = mock_components

    # Setup Mocks
    # 1. Brain
    brain.classify_and_rewrite.return_value = (
        UserIntent(
            intent=IntentType.GENERAL_QUERY,
            targets=[],
            reasoning="test",
            entities=[]
        ),
        "rewritten query"
    )

    # 2. Retrieval
    chunk = Chunk(id="1", content="text", parent_id="d1", index=0, metadata={"source": "test"})
    retrieval.hybrid_search.return_value = ([chunk], [], [])

    # 3. Reranker
    reranker.rerank.return_value = ([chunk], [])

    # Execute
    final_state = await orchestrator.run_pipeline(
        query="test query",
        history=[],
        config={"configurable": {"retrieval_config": {"top_k": 3}}}
    )

    # Verify Flow
    brain.classify_and_rewrite.assert_called_once()
    retrieval.hybrid_search.assert_called_once()
    reranker.rerank.assert_called_once()
    generator.generate_answer.assert_called_once()

    assert final_state["final_answer"] == "Final Answer"
    assert len(final_state["vector_chunks"]) == 1

@pytest.mark.asyncio
async def test_run_pipeline_fallback(orchestrator, mock_components):
    brain, reranker, generator, retrieval = mock_components

    # Setup Mocks
    brain.classify_and_rewrite.return_value = (
        UserIntent(
            intent=IntentType.FILTER_BY_TOPIC,
            targets=["topic"],
            reasoning="test",
            entities=[]
        ),
        "rewritten"
    )

    # First search returns empty with filters
    # Second search (fallback) returns results
    chunk = Chunk(id="1", content="text", parent_id="d1", index=0, metadata={"source": "test"})

    # AsyncMock side_effect for multiple calls
    retrieval.hybrid_search.side_effect = [
        ([], [], []), # First call (empty)
        ([chunk], [], []) # Second call (fallback)
    ]

    reranker.rerank.return_value = ([chunk], [])

    # Execute
    # We pass manual_filters to ensure filter logic runs
    final_state = await orchestrator.run_pipeline(
        query="test",
        history=[],
        config={},
        manual_filters={"topic": "topic"}
    )

    # Verify Fallback Triggered
    # Retrieval should be called twice
    assert retrieval.hybrid_search.call_count == 2
    assert final_state.get("fallback_triggered") is True
    assert len(final_state["vector_chunks"]) == 1
