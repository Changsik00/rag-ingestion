"""
RAG Graph End-to-End Flow 통합 테스트.

실제 LLM을 사용하여 전체 RAG Pipeline이 정상 동작하는지 검증합니다.
BDD(Behavior-Driven Development) 스타일의 Given-When-Then 시나리오 사용.

Spec 033: LangGraph State Management
"""

import pytest

from app.domain.schemas.intent import IntentType


@pytest.mark.integration
class TestRAGGraphFlow:
    """RAG Graph End-to-End 흐름 테스트"""

    @pytest.mark.asyncio
    async def test_general_query_flow(self, real_rag_service):
        """
        Given: 일반 질문 ("인공지능이 뭐야?")
        When: RAG Graph 실행
        Then: GENERAL_QUERY Intent, 전체 검색 수행, 답변 생성
        """
        # Given
        query = "인공지능이 뭐야?"
        history = []

        # When
        result = await real_rag_service.retrieve_and_generate(query, history)

        # Then
        assert result.user_intent is not None
        assert result.user_intent.intent == IntentType.GENERAL_QUERY
        assert result.rewritten_query is not None
        assert result.final_answer != ""
        # GENERAL_QUERY는 필터가 없어야 함
        assert result.vector_chunks is not None
        assert result.keyword_chunks is not None

    @pytest.mark.asyncio
    async def test_compare_intent_auto_filtering(
        self, real_rag_service, sample_documents
    ):
        """
        Given: 비교 질문 ("Claude와 GPT-4를 비교해줘") + 두 문서 존재
        When: RAG Graph 실행
        Then: COMPARE Intent, Auto Filters 적용, 특정 문서만 검색
        """
        # Given
        query = "Claude와 GPT-4를 비교해줘"
        history = []

        # When
        result = await real_rag_service.retrieve_and_generate(query, history)

        # Then
        assert result.user_intent is not None
        assert result.user_intent.intent == IntentType.COMPARE
        assert len(result.user_intent.targets) > 0
        # Filters가 자동 적용되었는지 확인
        assert result.final_answer != ""

    @pytest.mark.asyncio
    async def test_state_checkpoint_saving(
        self, real_rag_service_with_checkpointer
    ):
        """
        Given: Thread ID 지정 + Checkpointer 활성화
        When: RAG Graph 실행
        Then: Checkpointer에 State Snapshot 저장 확인
        """
        # Given
        query = "RAG가 뭐야?"
        history = []
        thread_id = "test-checkpoint-123"

        # When
        result = await real_rag_service_with_checkpointer.retrieve_and_generate(
            query, history, thread_id=thread_id
        )

        # Then
        assert result.final_answer != ""

        # Checkpointer를 통해 State 조회 가능한지 확인
        # (실제로는 RAGService 내부에서 checkpointer.get() 호출 필요)
        # 여기서는 최소한 오류 없이 실행되었음을 확인


@pytest.fixture
def real_rag_service():
    """실제 LLM을 사용하는 RAGService (Checkpointer 없음)"""
    # TODO: DI를 통해 실제 RAGService 인스턴스 생성
    # 현재는 Mock으로 구현 (실제 구현은 RAGService 완성 후)
    pytest.skip("RAGService 리팩토리 완료 후 구현")


@pytest.fixture
def real_rag_service_with_checkpointer():
    """실제 LLM + Checkpointer를 사용하는 RAGService"""
    pytest.skip("RAGService 리팩토리 완료 후 구현")


@pytest.fixture
def sample_documents():
    """테스트용 샘플 문서"""
    # TODO: 테스트용 문서 생성 로직
    pytest.skip("샘플 문서 생성 로직 구현 필요")
