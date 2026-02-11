import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.domain.services.intent_classifier import IntentClassifier
from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import IntentType
from app.infrastructure.repositories.chroma import ChromaVectorRepository
from app.infrastructure.repositories.neo4j_document_repository import Neo4jDocumentRepository
from app.infrastructure.repositories.neo4j_graph_repository import Neo4jGraphRepository
from app.interfaces.api.dependencies import get_neo4j_driver


@pytest.fixture(scope="module")
def driver():
    return get_neo4j_driver()


@pytest.fixture(scope="module")
def chroma_repo():
    return ChromaVectorRepository()


@pytest.fixture(scope="module")
def neo4j_repo(driver):
    return Neo4jDocumentRepository(driver)


@pytest.fixture(scope="module")
def graph_repo(driver):
    return Neo4jGraphRepository(driver)


@pytest.fixture
def mock_llm_intent():
    mock = MagicMock()

    async def agenerate(prompt: str):
        prompt_lower = prompt.lower()
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
class TestRetrievalLogic:
    """
    Functional tests for retrieval and search strategies.
    Pattern: Given-When-Then (GWT)
    """

    def test_hybrid_pipeline_components(self, neo4j_repo, graph_repo, chroma_repo):
        # Given: A common query term
        query = "Artificial Intelligence"

        # When: Executing Neo4j keyword search
        kw_results = neo4j_repo.search(query)
        # Then: Returns a valid list of chunks
        assert isinstance(kw_results, list)

        # When: Executing Graph subgraph retrieval
        graph_results = graph_repo.get_subgraph([query])
        # Then: Returns a valid adjacency list/dict structure
        assert isinstance(graph_results, list)

        # When: Executing Chroma MMR search
        vector_results = chroma_repo.search_mmr(query, limit=5)
        # Then: Returns a valid list of chunks
        assert isinstance(vector_results, list)

    def test_filtered_search_isolation(self, chroma_repo):
        # Given: Two documents with distinct topics ("Apple" as Brand vs Fruit)
        doc_tech_id = str(uuid4())
        doc_fruit_id = str(uuid4())

        chunks = [
            Chunk(id=str(uuid4()), content="Apple macOS is an operating system.", parent_id=doc_tech_id, index=0),
            Chunk(
                id=str(uuid4()), content="Apple is a red edible fruit with high fiber.", parent_id=doc_fruit_id, index=0
            ),
        ]
        chroma_repo.save_chunks(chunks)

        # When: Searching for "Apple" filtered by Tech document
        tech_results = chroma_repo.search("Apple", limit=5, filters={"doc_id": doc_tech_id})

        # Then: Only the Tech chunk is found
        assert len(tech_results) > 0
        assert all(str(c.parent_id) == doc_tech_id for c in tech_results)
        assert any("macOS" in c.content for c in tech_results)
        assert not any("fruit" in c.content for c in tech_results)

        # When: Searching for "Apple" filtered by Fruit document
        fruit_results = chroma_repo.search("Apple", limit=5, filters={"doc_id": doc_fruit_id})

        # Then: Only the Fruit chunk is found
        assert len(fruit_results) > 0
        assert all(str(c.parent_id) == doc_fruit_id for c in fruit_results)
        assert any("fruit" in c.content for c in fruit_results)
        assert not any("macOS" in c.content for c in fruit_results)

    def test_graph_navigation_retrieval(self, graph_repo):
        # Given: A set of entities (A -> B)
        # (Assuming these were seeded or dynamically created if repo supports it)
        # For functional test, we verify the capability to query neighbors

        # When: Requesting neighbors for a known entity
        neighbors = graph_repo.get_entity_relationships("Python")

        # Then: Returns a valid list structure (even if empty in clean state)
        assert isinstance(neighbors, list)

    @pytest.mark.asyncio
    async def test_intent_classifier_contextual_history(self, mock_llm_intent):
        """
        Component Test: Intent classification with conversation history (Spec-012)
        """
        classifier = IntentClassifier(mock_llm_intent)

        # Given: A follow-up query that relies on history
        query = "GPT-4랑 비교해줘"
        history = [
            {"role": "user", "content": "Claude에 대해 알려줘"},
            {"role": "assistant", "content": "Claude는 Anthropic이 만든 AI입니다."},
        ]

        # When: Classifying the intent
        intent = await classifier.classify(query, history)

        # Then: Intent is COMPARE and contains targets from history
        assert intent.intent == IntentType.COMPARE
        assert any("claude" in t.lower() for t in intent.targets)

    @pytest.mark.asyncio
    async def test_intent_classifier_summarize_with_pronoun(self, mock_llm_intent):
        """
        Component Test: Summarize 'this' document mentioned in history
        """
        classifier = IntentClassifier(mock_llm_intent)

        # Given: "Summarize this" after a specific document mention
        query = "이 문서 요약해줘"
        history = [
            {"role": "user", "content": "LangChain 문서 보여줘"},
            {"role": "assistant", "content": "LangChain 문서를 찾았습니다."},
        ]

        # When: Classifying the intent
        intent = await classifier.classify(query, history)

        # Then: Intent is SUMMARIZE and target is LangChain
        assert intent.intent == IntentType.SUMMARIZE
        assert any("langchain" in t.lower() for t in intent.targets)

    def test_select_strategy_logic(self):
        """
        Technical Test: Feedback-driven strategy selection
        """
        from app.domain.value_objects.ingestion_state import StrategyType, ValidationFeedback
        from app.infrastructure.ai.ingest.nodes import select_strategy

        # Given: Feedback indicating poor results
        feedback = [ValidationFeedback(source="validator", message="poor content", target_fields=[])]

        # When: First failure (retry_count=0)
        strategy = select_strategy(retry_count=0, feedbacks=feedback)

        # Then: Strategy is CORRECTION
        assert strategy == StrategyType.CORRECTION

        # When: Repeated failure (retry_count=2)
        strategy = select_strategy(retry_count=2, feedbacks=feedback)

        # Then: Strategy is RELAXATION
        assert strategy == StrategyType.RELAXATION
