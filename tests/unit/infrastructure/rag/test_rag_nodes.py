"""
RAG Nodes 비즈니스 로직 단위 테스트.

각 노드가 RAGGraphState를 올바르게 업데이트하는지 검증합니다.
Mock LLM을 사용하여 외부 의존성 없이 독립적으로 테스트합니다.

Spec 033: LangGraph State Management
"""

from unittest.mock import AsyncMock, Mock

import pytest

from app.domain.entities.chunk import Chunk
from app.domain.schemas.intent import IntentType, UserIntent


@pytest.fixture
def mock_llm():
    """Mock LLM Interface"""
    return Mock()


@pytest.fixture
def mock_query_rewriter():
    """Mock Query Rewriter"""
    rewriter = Mock()
    rewriter.rewrite.return_value = "재작성된 질문"
    return rewriter


@pytest.fixture
def mock_intent_classifier():
    """Mock Intent Classifier"""
    classifier = Mock()
    classifier.classify.return_value = UserIntent(
        intent=IntentType.GENERAL_QUERY,
        targets=[],
        reasoning="일반 질문"
    )
    return classifier


@pytest.fixture
def mock_repositories():
    """Mock Repositories (Neo4j, Chroma)"""
    neo4j_doc = Mock()
    neo4j_doc.search = AsyncMock(return_value=[])
    
    neo4j_graph = Mock()
    neo4j_graph.get_subgraph = AsyncMock(return_value=[])
    
    chroma = Mock()
    chroma.search_mmr = AsyncMock(return_value=[])
    
    return {
        "neo4j_doc": neo4j_doc,
        "neo4j_graph": neo4j_graph,
        "chroma": chroma
    }


class TestRAGNodesClassifyIntent:
    """classify_intent 노드 테스트"""
    
    def test_updates_state_with_intent_and_rewritten_query(
        self, mock_llm, mock_query_rewriter, mock_intent_classifier, mock_repositories
    ):
        """
        Given: 초기 RAG State (query, history)
        When: classify_intent 노드 실행
        Then: user_intent와 rewritten_query가 State에 추가됨
        """
        from app.infrastructure.rag.nodes import RAGNodes
        
        nodes = RAGNodes(
            neo4j_doc_repo=mock_repositories["neo4j_doc"],
            neo4j_graph_repo=mock_repositories["neo4j_graph"],
            chroma_repo=mock_repositories["chroma"],
            query_rewriter=mock_query_rewriter,
            intent_classifier=mock_intent_classifier,
            llm=mock_llm
        )
        
        # Given
        state = {
            "query": "인공지능이 뭐야?",
            "history": [],
            "manual_filters": None,
            "user_intent": None,
            "rewritten_query": None,
            "auto_filters": None,
            "final_filters": None,
            "vector_chunks": [],
            "keyword_chunks": [],
            "graph_data": [],
            "full_context": "",
            "final_answer": ""
        }
        
        # When
        result = nodes.classify_intent(state)
        
        # Then
        assert result["user_intent"] is not None
        assert result["user_intent"].intent == IntentType.GENERAL_QUERY
        assert result["rewritten_query"] == "재작성된 질문"
        mock_query_rewriter.rewrite.assert_called_once_with("인공지능이 뭐야?", [])
        mock_intent_classifier.classify.assert_called_once_with("인공지능이 뭐야?", [])


class TestRAGNodesRouteDecision:
    """route_decision 노드 테스트"""
    
    def test_converts_intent_to_auto_filters(
        self, mock_llm, mock_query_rewriter, mock_intent_classifier, mock_repositories
    ):
        """
        Given: COMPARE Intent가 포함된 State
        When: route_decision 노드 실행
        Then: auto_filters가 Intent로부터 도출됨
        """
        from app.infrastructure.rag.nodes import RAGNodes
        
        nodes = RAGNodes(
            neo4j_doc_repo=mock_repositories["neo4j_doc"],
            neo4j_graph_repo=mock_repositories["neo4j_graph"],
            chroma_repo=mock_repositories["chroma"],
            query_rewriter=mock_query_rewriter,
            intent_classifier=mock_intent_classifier,
            llm=mock_llm
        )
        
        # Given
        state = {
            "query": "Claude와 GPT-4를 비교해줘",
            "history": [],
            "manual_filters": None,
            "user_intent": UserIntent(
                intent=IntentType.COMPARE,
                targets=["claude", "gpt-4"],
                reasoning="비교 요청"
            ),
            "rewritten_query": "Claude AI와 GPT-4의 특징 비교",
            "auto_filters": None,
            "final_filters": None,
            "vector_chunks": [],
            "keyword_chunks": [],
            "graph_data": [],
            "full_context": "",
            "final_answer": ""
        }
        
        # When
        result = nodes.route_decision(state)
        
        # Then
        assert result["auto_filters"] is not None
        assert result["auto_filters"] == {"source": ["claude", "gpt-4"]}
        assert result["final_filters"] == {"source": ["claude", "gpt-4"]}
    
    def test_prioritizes_manual_filters_over_auto(
        self, mock_llm, mock_query_rewriter, mock_intent_classifier, mock_repositories
    ):
        """
        Given: Manual Filters와 Auto Filters가 모두 존재하는 State
        When: route_decision 노드 실행
        Then: Manual Filters가 우선 적용됨 (Auto Filters 무시)
        """
        from app.infrastructure.rag.nodes import RAGNodes
        
        nodes = RAGNodes(
            neo4j_doc_repo=mock_repositories["neo4j_doc"],
            neo4j_graph_repo=mock_repositories["neo4j_graph"],
            chroma_repo=mock_repositories["chroma"],
            query_rewriter=mock_query_rewriter,
            intent_classifier=mock_intent_classifier,
            llm=mock_llm
        )
        
        # Given
        manual_filters = {"source": ["doc_A"]}
        state = {
            "query": "Claude와 GPT-4를 비교해줘",
            "history": [],
            "manual_filters": manual_filters,
            "user_intent": UserIntent(
                intent=IntentType.COMPARE,
                targets=["claude", "gpt-4"],
                reasoning="비교 요청"
            ),
            "rewritten_query": "Claude AI와 GPT-4의 특징 비교",
            "auto_filters": None,
            "final_filters": None,
            "vector_chunks": [],
            "keyword_chunks": [],
            "graph_data": [],
            "full_context": "",
            "final_answer": ""
        }
        
        # When
        result = nodes.route_decision(state)
        
        # Then
        assert result["final_filters"] == manual_filters  # Manual이 우선


class TestRAGNodesRetrieveHybrid:
    """retrieve_hybrid 노드 테스트"""
    
    @pytest.mark.asyncio
    async def test_parallel_search_updates_all_chunks(
        self, mock_llm, mock_query_rewriter, mock_intent_classifier, mock_repositories
    ):
        """
        Given: rewritten_query와 final_filters가 설정된 State
        When: retrieve_hybrid 노드 실행
        Then: vector_chunks, keyword_chunks, graph_data가 모두 State에 추가됨
        """
        from app.infrastructure.rag.nodes import RAGNodes
        
        # Mock 검색 결과
        mock_chunk = Chunk(
            id="chunk_1",
            content="테스트 내용",
            document_id="doc_1",
            metadata={"source": "test.com", "title": "Test"}
        )
        
        mock_repositories["chroma"].search_mmr.return_value = [mock_chunk]
        mock_repositories["neo4j_doc"].search.return_value = [mock_chunk]
        mock_repositories["neo4j_graph"].get_subgraph.return_value = [
            {"source": "Entity1", "relationship": "RELATED_TO", "target": "Entity2"}
        ]
        
        nodes = RAGNodes(
            neo4j_doc_repo=mock_repositories["neo4j_doc"],
            neo4j_graph_repo=mock_repositories["neo4j_graph"],
            chroma_repo=mock_repositories["chroma"],
            query_rewriter=mock_query_rewriter,
            intent_classifier=mock_intent_classifier,
            llm=mock_llm
        )
        
        # Given
        state = {
            "query": "인공지능이 뭐야?",
            "history": [],
            "manual_filters": None,
            "user_intent": UserIntent(
                intent=IntentType.GENERAL_QUERY,
                targets=[],
                reasoning="일반 질문"
            ),
            "rewritten_query": "인공지능의 정의와 개념",
            "auto_filters": None,
            "final_filters": None,
            "vector_chunks": [],
            "keyword_chunks": [],
            "graph_data": [],
            "full_context": "",
            "final_answer": ""
        }
        
        # When
        result = await nodes.retrieve_hybrid(state)
        
        # Then
        assert len(result["vector_chunks"]) == 1
        assert len(result["keyword_chunks"]) == 1
        assert len(result["graph_data"]) == 1
        assert result["vector_chunks"][0].id == "chunk_1"


class TestRAGNodesGenerateAnswer:
    """generate_answer 노드 테스트"""
    
    def test_formats_context_and_generates_answer(
        self, mock_llm, mock_query_rewriter, mock_intent_classifier, mock_repositories
    ):
        """
        Given: 검색 결과(chunks, graph_data)가 포함된 State
        When: generate_answer 노드 실행
        Then: full_context와 final_answer가 State에 추가됨
        """
        from unittest.mock import Mock
        from app.infrastructure.rag.nodes import RAGNodes
        
        # Mock LLM Response
        mock_response = Mock()
        mock_response.content = "인공지능은 기계가 인간처럼 학습하고 판단하는 기술입니다."
        mock_llm.generate.return_value = mock_response
        
        nodes = RAGNodes(
            neo4j_doc_repo=mock_repositories["neo4j_doc"],
            neo4j_graph_repo=mock_repositories["neo4j_graph"],
            chroma_repo=mock_repositories["chroma"],
            query_rewriter=mock_query_rewriter,
            intent_classifier=mock_intent_classifier,
            llm=mock_llm
        )
        
        # Given
        chunk = Chunk(
            id="chunk_1",
            content="AI는 인공지능을 의미합니다.",
            document_id="doc_1",
            metadata={"source": "test.com", "title": "AI 개념"}
        )
        
        state = {
            "query": "인공지능이 뭐야?",
            "history": [],
            "manual_filters": None,
            "user_intent": UserIntent(
                intent=IntentType.GENERAL_QUERY,
                targets=[],
                reasoning="일반 질문"
            ),
            "rewritten_query": "인공지능의 정의",
            "auto_filters": None,
            "final_filters": None,
            "vector_chunks": [chunk],
            "keyword_chunks": [],
            "graph_data": [{"source": "AI", "relationship": "IS_A", "target": "Technology"}],
            "full_context": "",
            "final_answer": ""
        }
        
        # When
        result = nodes.generate_answer(state)
        
        # Then
        assert result["full_context"] != ""
        assert "test.com" in result["full_context"]  # Citation 포함
        assert result["final_answer"] == "인공지능은 기계가 인간처럼 학습하고 판단하는 기술입니다."
        mock_llm.generate.assert_called_once()
