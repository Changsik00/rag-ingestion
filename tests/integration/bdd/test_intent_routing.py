import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.value_objects.intent import IntentType


class MockLLM:
    """Mock LLM for Intent Routing Tests"""
    
    async def agenerate(self, prompt: str):
        prompt_lower = prompt.lower()
        
        # 1. Compare Claude vs GPT-4
        if "claude" in prompt_lower and "gpt-4" in prompt_lower and "비교" in prompt_lower:
            return MagicMock(__str__=lambda x: json.dumps({
                "intent": "compare",
                "targets": ["Claude", "GPT-4"],
                "entities": ["Claude", "GPT-4"],
                "reasoning": "Comparing two models mentioned in query."
            }))
        
        # 3. Contextual Compare (GPT-4 vs History Claude)
        # History is embedded in prompt. 
        if "gpt-4" in prompt_lower and "비교" in prompt_lower and "claude" in prompt_lower:
            # (Matches logic above essentially, but explicit for clarity)
            return MagicMock(__str__=lambda x: json.dumps({
                "intent": "compare",
                "targets": ["Claude", "GPT-4"],
                "entities": ["Claude", "GPT-4"],
                "reasoning": "Comparing GPT-4 from query with Claude from history."
            }))

        # 4. Summarize "this document" (LangChain)
        if "요약해줘" in prompt_lower and "langchain" in prompt_lower:
             return MagicMock(__str__=lambda x: json.dumps({
                "intent": "summarize",
                "targets": ["LangChain"],
                "entities": ["LangChain"],
                "reasoning": "Summarizing document mentioned in history."
            }))
             
        # 5. Filter by Topic (Python)
        if "python" in prompt_lower:
             return MagicMock(__str__=lambda x: json.dumps({
                "intent": "filter_by_topic",
                "targets": ["Python"],
                "entities": ["Python"],
                "reasoning": "Filtering by Python topic."
            }))

        # 2. General Query
        return MagicMock(__str__=lambda x: json.dumps({
            "intent": "general_query",
            "targets": [],
            "entities": [],
            "reasoning": "General question."
        }))


@pytest.fixture
def mock_llm():
    return MockLLM()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_with_mock_llm(mock_llm):
    """
    Given: Mock LLM이 연결된 IntentClassifier
    When: 비교 의도가 명확한 쿼리를 입력
    Then: COMPARE Intent와 정확한 targets를 반환해야 함
    """
    classifier = IntentClassifier(mock_llm)
    query = "Claude와 GPT-4를 비교해줘"
    history = []
    
    result = await classifier.classify(query, history)
    
    assert result.intent == IntentType.COMPARE
    targets_lower = [t.lower() for t in result.targets]
    assert "claude" in targets_lower
    assert "gpt-4" in targets_lower


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_general_query_with_mock_llm(mock_llm):
    """
    Given: Mock LLM
    When: 일반 질문 입력
    Then: GENERAL_QUERY Intent 반환
    """
    classifier = IntentClassifier(mock_llm)
    query = "인공지능이 뭐야?"
    history = []
    
    result = await classifier.classify(query, history)
    
    assert result.intent == IntentType.GENERAL_QUERY
    assert len(result.targets) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_with_history_context(mock_llm):
    """
    Given: 대화 히스토리가 있는 상태
    When: "그거랑 비교해줘" 같은 대명사 질문 입력
    """
    classifier = IntentClassifier(mock_llm)
    query = "GPT-4랑 비교해줘"
    history = [
        {"role": "user", "content": "Claude에 대해 알려줘"},
        {"role": "assistant", "content": "Claude는 Anthropic이 만든 대화형 AI입니다."},
    ]
    
    # Prompt will contain history, so MockLLM checks for 'claude' in prompt
    result = await classifier.classify(query, history)
    
    assert result.intent == IntentType.COMPARE
    assert len(result.targets) >= 1 # At least GPT-4, ideally Claude too if extracted


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_summarize_with_pronoun(mock_llm):
    """
    Given: 특정 문서에 대한 대화 후
    When: "이 문서 요약해줘" 입력
    """
    classifier = IntentClassifier(mock_llm)
    query = "이 문서 요약해줘"
    history = [
        {"role": "user", "content": "LangChain 문서 보여줘"},
        {"role": "assistant", "content": "LangChain 공식 문서를 찾았습니다."},
    ]
    
    result = await classifier.classify(query, history)
    
    assert result.intent == IntentType.SUMMARIZE
    targets_lower = [t.lower() for t in result.targets]
    assert "langchain" in targets_lower


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intent_classifier_filter_by_topic(mock_llm):
    """
    Given: IntentClassifier
    When: 특정 주제로 필터링 요청
    """
    classifier = IntentClassifier(mock_llm)
    query = "Python 관련된 것만 보여줘"
    history = []
    
    result = await classifier.classify(query, history)
    
    assert result.intent == IntentType.FILTER_BY_TOPIC
    targets_lower = [t.lower() for t in result.targets]
    assert "python" in targets_lower
