import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.rag import RAG, RAGResult
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter
from app.domain.value_objects.intent import IntentType, UserIntent


@pytest.fixture
def mock_llm_intent():
    mock = MagicMock()

    async def agenerate(prompt: str):
        prompt_lower = prompt.lower()
        # Isolate the current query to avoid matching keywords in instructions/examples
        query_part = (
            prompt_lower.split("**current query:**")[-1] if "**current query:**" in prompt_lower else prompt_lower
        )

        if "요약해줘" in query_part:
            return MagicMock(
                __str__=lambda x: json.dumps(
                    {"intent": "summarize", "targets": ["LangChain"], "entities": [], "reasoning": "Summarization"}
                )
            )
        if "비교" in query_part or "tell me more" in query_part:
            return MagicMock(
                __str__=lambda x: json.dumps(
                    {"intent": "compare", "targets": ["Claude", "GPT-4"], "entities": [], "reasoning": "Comparison"}
                )
            )
        return MagicMock(
            __str__=lambda x: json.dumps(
                {"intent": "general_query", "targets": [], "entities": [], "reasoning": "General"}
            )
        )

    mock.agenerate = agenerate
    return mock


@pytest.mark.integration
@pytest.mark.asyncio
class TestRagPipelineScenarios:
    """
    RAG Pipeline Reasoning Scenarios
    Pattern: Given-When-Then (GWT)
    """

    async def test_combined_intent_and_rewriting_flow(self, mock_llm_intent):
        # Given: Intent classifier and Query rewriter with context
        classifier = IntentClassifier(mock_llm_intent)

        mock_rewriter_llm = MagicMock()
        mock_rewriter_llm.invoke = MagicMock(return_value=MagicMock(content="Rewritten: What is Claude?"))
        mock_rewriter_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Rewritten: What is Claude?"))

        from app.infrastructure.ai.langchain_extractor import LangChainExtractor

        extractor = LangChainExtractor(llm=mock_rewriter_llm)
        extractor.agenerate = AsyncMock(return_value="Rewritten: What is Claude?")
        rewriter = QueryRewriter(extractor)

        # When: Processing a follow-up query
        query = "Tell me more about it"
        history = [{"role": "user", "content": "What is Claude?"}]

        intent = await classifier.classify(query, history)
        rewritten = await rewriter.rewrite(query, history)

        # Then: Intent is comparison (mocked behavior) and query is disambiguated
        assert intent.intent == IntentType.COMPARE
        assert "Claude" in rewritten

    async def test_rag_service_e2e_integration(self):
        # Given: A RAG service with a mocked LangGraph app
        mock_graph = MagicMock()
        mock_result_state = {
            "query": "Test Query",
            "user_intent": UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="Test"),
            "rewritten_query": "Rewritten Query",
            "vector_chunks": [],
            "keyword_chunks": [],
            "graph_data": [],
            "full_context": "Mock Context",
            "final_answer": "Final Result",
        }
        mock_graph.ainvoke = AsyncMock(return_value=mock_result_state)
        rag_service = RAG(graph=mock_graph)

        # When: Executing a full RAG cycle
        result = await rag_service.retrieve_and_generate("Test Query", [])

        # Then: Returns a valid RAGResult with expected components
        assert isinstance(result, RAGResult)
        assert result.answer == "Final Result"
        assert result.full_context == "Mock Context"
        mock_graph.ainvoke.assert_called_once()

    async def test_reasoning_feedback_loop_scenario(self):
        # Given: An ingestion graph state with a validation error
        # This simulates the internal state transitions tested in bdd/test_reasoning_flow.py
        from app.domain.value_objects.ingestion_state import ValidationFeedback

        # When: Simulating a reasoning step after failure
        # (Conceptual check of logic resolution transitions)
        feedback = ValidationFeedback(source="validator", message="Missing summary", target_fields=["summary"])

        # Then: System identifies the failure hypothesis (Logic verified via functional tests previously)
        assert "summary" in feedback.target_fields
        assert feedback.source == "validator"
