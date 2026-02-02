import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import IntentType, UserIntent
from app.infrastructure.ai.rag_graph import RAGGraphBuilder
from app.infrastructure.ai.rag_nodes import RAGNodes

# pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


@pytest.mark.asyncio
async def test_rag_precision_refinement_flow():
    """
    [Spec 048] Integration Test.
    검색 결과가 LLM Reranker에 의해 필터링되고 최종 답변 생성에 반영되는지 확인합니다.
    """
    # 1. Mock Repositories
    mock_chroma = MagicMock()
    mock_neo4j_doc = MagicMock()
    mock_neo4j_graph = MagicMock()
    mock_llm = MagicMock()
    mock_rewriter = MagicMock()
    mock_classifier = MagicMock()

    # Query Rewriting
    mock_rewriter.rewrite = AsyncMock(return_value="Rewritten Query")
    # Intent Classification
    mock_classifier.classify = AsyncMock(
        return_value=UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Test")
    )

    # Search Results (2 Chunks: 1 Highly Relevant, 1 Lowly Relevant)
    relevant_chunk = Chunk(
        id="rel-1", content="This is highly relevant content.", parent_id="doc-1", index=0, metadata={"title": "T1"}
    )
    irrelevant_chunk = Chunk(
        id="irr-1", content="This is completely irrelevant spam.", parent_id="doc-2", index=0, metadata={"title": "T2"}
    )

    mock_chroma.search_mmr.return_value = [relevant_chunk, irrelevant_chunk]
    mock_neo4j_doc.search.return_value = []
    mock_neo4j_graph.get_subgraph.return_value = []

    # LLM Reranking & Answer Generation
    # 1st call: Reranking rel-1 (score 9)
    # 2nd call: Reranking irr-1 (score 1)
    # 3rd call: Answer Generation
    mock_llm.agenerate = AsyncMock(
        side_effect=[
            MagicMock(content=json.dumps({"score": 9, "reasoning": "Direct answer"})),
            MagicMock(content=json.dumps({"score": 1, "reasoning": "Irrelevant noise"})),
            MagicMock(content="Final Precision Answer [1]"),
        ]
    )

    # 2. Setup Graph
    nodes = RAGNodes(
        neo4j_doc_repo=mock_neo4j_doc,
        neo4j_graph_repo=mock_neo4j_graph,
        chroma_repo=mock_chroma,
        query_rewriter=mock_rewriter,
        intent_classifier=mock_classifier,
        llm=mock_llm,
    )

    builder = RAGGraphBuilder(nodes)
    graph = builder.build()

    # 3. Execute
    initial_state = {
        "query": "Precision Test",
        "history": [],
        "manual_filters": None,
        "vector_chunks": [],
        "keyword_chunks": [],
        "graph_data": [],
        "reranked_chunks": None,
        "rerank_log": [],
        "reasoning_log": [],
        "full_context": "",
        "final_answer": "",
    }

    final_state = await graph.ainvoke(initial_state)

    # 4. Verify
    # - Reranked chunks should only have 1 chunk (rel-1) since irr-1 (score 1) is below threshold 5
    assert len(final_state["reranked_chunks"]) == 1
    assert final_state["reranked_chunks"][0].id == "rel-1"

    # - Final Answer should be the precision one
    assert final_state["final_answer"] == "Final Precision Answer [1]"

    # - Context given to LLM for Answer Generation should ONLY contain rel-1
    # We check the third call to llm.agenerate
    answer_gen_prompt = mock_llm.agenerate.call_args_list[2][0][0]
    assert "This is highly relevant content." in answer_gen_prompt
    assert "This is completely irrelevant spam." not in answer_gen_prompt

    print("Graph Precision Refinement Verified Successfully.")
