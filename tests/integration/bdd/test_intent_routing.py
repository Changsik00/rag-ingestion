import os

import pytest
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.domain.schemas.intent import IntentType
from app.domain.services.intent_classifier import IntentClassifier
from app.infrastructure.llm.langchain_adapter import LangChainLLMAdapter

load_dotenv()

"""
Integration Test: Intent Routing
BDD 스타일로 Intent Classifier와 RAG Service의 통합을 검증한다.
"""


@pytest.fixture
def llm_adapter():
    """실제 LLM Adapter Fixture"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not found")

    base_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    return LangChainLLMAdapter(base_llm)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_with_real_llm(llm_adapter):
    """
    Given: 실제 LLM이 연결된 IntentClassifier
    When: 비교 의도가 명확한 쿼리를 입력
    Then: COMPARE Intent와 정확한 targets를 반환해야 함

    User Story:
    사용자가 "Claude와 GPT-4를 비교해줘"라고 입력하면
    시스템이 자동으로 두 문서를 타겟으로 지정해야 한다.
    """
    # Given
    classifier = IntentClassifier(llm_adapter)

    query = "Claude와 GPT-4를 비교해줘"
    history = []

    # When
    result = await classifier.classify(query, history)

    # Then
    assert result.intent == IntentType.COMPARE
    # Normalize to lowercase for comparison
    targets_lower = [t.lower() for t in result.targets]
    assert "claude" in targets_lower
    assert "gpt" in targets_lower or "gpt-4" in targets_lower
    assert len(result.targets) >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_general_query_with_real_llm(llm_adapter):
    """
    Given: 실제 LLM이 연결된 IntentClassifier
    When: 특정 타겟이 없는 일반 질문 입력
    Then: GENERAL_QUERY Intent와 빈 targets 반환

    User Story:
    "인공지능이 뭐야?" 같은 일반 질문에는 전체 지식베이스를 검색해야 한다.
    """
    # Given
    classifier = IntentClassifier(llm_adapter)

    query = "인공지능이 뭐야?"
    history = []

    # When
    result = await classifier.classify(query, history)

    # Then
    assert result.intent == IntentType.GENERAL_QUERY
    assert len(result.targets) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_with_history_context(llm_adapter):
    """
    Given: 대화 히스토리가 있는 상태
    When: "그거랑 비교해줘" 같은 대명사 질문 입력
    Then: 히스토리에서 타겟을 추출하여 COMPARE Intent 반환

    User Story:
    "Claude는 어때?" → "GPT-4랑 비교해줘"처럼 연속된 질문에서
    시스템이 이전 문맥을 이해해야 한다.
    """
    # Given
    base_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    llm = LangChainLLMAdapter(base_llm)
    classifier = IntentClassifier(llm)

    query = "GPT-4랑 비교해줘"
    history = [
        {"role": "user", "content": "Claude에 대해 알려줘"},
        {"role": "assistant", "content": "Claude는 Anthropic이 만든 대화형 AI입니다."},
    ]

    # When
    result = await classifier.classify(query, history)

    # Then
    assert result.intent == IntentType.COMPARE
    # LLM should infer "Claude" from history and "GPT-4" from current query
    targets_lower = [t.lower() for t in result.targets]
    assert "claude" in targets_lower or "gpt" in targets_lower


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_summarize_with_pronoun(llm_adapter):
    """
    Given: 특정 문서에 대한 대화 후
    When: "이 문서 요약해줘" 입력
    Then: SUMMARIZE Intent와 히스토리의 문서를 target으로 반환

    User Story:
    사용자가 대명사("이것", "그거")를 사용해도 시스템이 맥락을 파악해야 한다.
    """
    # Given
    base_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    llm = LangChainLLMAdapter(base_llm)
    classifier = IntentClassifier(llm)

    query = "이 문서 요약해줘"
    history = [
        {"role": "user", "content": "LangChain 문서 보여줘"},
        {"role": "assistant", "content": "LangChain 공식 문서를 찾았습니다."},
    ]

    # When
    result = await classifier.classify(query, history)

    # Then
    assert result.intent == IntentType.SUMMARIZE
    # LLM should extract "LangChain" from history
    assert len(result.targets) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_filter_by_topic(llm_adapter):
    """
    Given: IntentClassifier
    When: 특정 주제로 필터링 요청
    Then: FILTER_BY_TOPIC Intent와 주제를 target으로 반환

    User Story:
    "Python 관련된 것만 보여줘"라고 하면 Python 주제만 검색해야 한다.
    """
    # Given
    base_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)
    llm = LangChainLLMAdapter(base_llm)
    classifier = IntentClassifier(llm)

    query = "Python 관련된 것만 보여줘"
    history = []

    # When
    result = await classifier.classify(query, history)

    # Then
    assert result.intent == IntentType.FILTER_BY_TOPIC
    targets_lower = [t.lower() for t in result.targets]
    assert "python" in targets_lower
