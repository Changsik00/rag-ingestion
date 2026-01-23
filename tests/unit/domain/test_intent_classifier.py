from unittest.mock import Mock

import pytest

from app.domain.interfaces.llm import LLMInterface

# Import will succeed after implementation
try:
    from app.domain.services.intent_classifier import IntentClassifier
    from app.domain.schemas.intent import UserIntent, IntentType
except ImportError:
    IntentClassifier = None
    UserIntent = None
    IntentType = None


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_general_query():
    """
    특정 문서나 타겟이 없는 일반 질문은 GENERAL_QUERY로 분류되어야 한다.
    
    User Story:
    사용자가 "인공지능이 뭐야?"라고 물으면
    시스템은 전체 지식 베이스를 검색해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = '{"intent": "general_query", "targets": [], "reasoning": "No specific target mentioned"}'
    classifier = IntentClassifier(llm)
    
    query = "인공지능이 뭐야?"
    history = []
    
    # When
    result = classifier.classify(query, history)
    
    # Then
    assert result.intent == IntentType.GENERAL_QUERY
    assert result.targets == []
    assert "target" in result.reasoning.lower()
    llm.generate.assert_called_once()


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_compare_intent():
    """
    두 개 이상의 대상을 비교하는 질문은 COMPARE로 분류되어야 한다.
    
    User Story:
    사용자가 "Claude와 GPT-4를 비교해줘"라고 하면
    시스템은 해당 두 문서만 검색하여 비교 정보를 제공해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = '{"intent": "compare", "targets": ["claude", "gpt-4"], "reasoning": "User wants comparison between two models"}'
    classifier = IntentClassifier(llm)
    
    query = "Claude와 GPT-4를 비교해줘"
    history = []
    
    # When
    result = classifier.classify(query, history)
    
    # Then
    assert result.intent == IntentType.COMPARE
    assert "claude" in result.targets
    assert "gpt-4" in result.targets
    assert len(result.targets) == 2


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_summarize_intent():
    """
    특정 문서의 요약을 요청하면 SUMMARIZE로 분류되어야 한다.
    
    User Story:
    사용자가 "이 문서 요약해줘"라고 대화 중에 말하면
    시스템은 히스토리에서 언급된 문서만 검색하여 요약해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = '{"intent": "summarize", "targets": ["langchain-docs"], "reasoning": "User requests summary of previously mentioned document"}'
    classifier = IntentClassifier(llm)
    
    query = "이 문서 요약해줘"
    history = [
        {"role": "user", "content": "LangChain 문서 보여줘"},
        {"role": "assistant", "content": "LangChain 관련 문서를 찾았습니다."}
    ]
    
    # When
    result = classifier.classify(query, history)
    
    # Then
    assert result.intent == IntentType.SUMMARIZE
    assert len(result.targets) > 0


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_filter_by_topic():
    """
    특정 주제나 카테고리로 필터링하는 질문은 FILTER_BY_TOPIC으로 분류되어야 한다.
    
    User Story:
    사용자가 "Python 관련된 것만 보여줘"라고 하면
    시스템은 Python 주제의 문서만 검색해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = '{"intent": "filter_by_topic", "targets": ["python"], "reasoning": "User wants to filter by Python topic"}'
    classifier = IntentClassifier(llm)
    
    query = "Python 관련된 것만 보여줘"
    history = []
    
    # When
    result = classifier.classify(query, history)
    
    # Then
    assert result.intent == IntentType.FILTER_BY_TOPIC
    assert "python" in result.targets


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_with_invalid_json_raises_exception():
    """
    LLM이 잘못된 JSON을 반환하면 예외를 발생시켜야 한다.
    (Caller가 Fallback 처리를 할 수 있도록)
    
    User Story:
    LLM 응답이 파싱 불가능하면 시스템은 안전하게 Fallback해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = "This is not a JSON"
    classifier = IntentClassifier(llm)
    
    query = "뭐든지 좋으니까 알려줘"
    history = []
    
    # When / Then
    with pytest.raises(Exception):  # JSONDecodeError or ValidationError
        classifier.classify(query, history)


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_with_invalid_intent_type_raises_validation_error():
    """
    Pydantic Schema에 정의되지 않은 Intent Type이 오면 ValidationError가 발생해야 한다.
    
    User Story:
    LLM이 잘못된 intent를 반환해도 시스템은 타입 안전성을 보장해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = '{"intent": "INVALID_TYPE", "targets": [], "reasoning": "Test"}'
    classifier = IntentClassifier(llm)
    
    query = "테스트 쿼리"
    history = []
    
    # When / Then
    with pytest.raises(Exception):  # Pydantic ValidationError
        classifier.classify(query, history)


@pytest.mark.skipif(IntentClassifier is None, reason="IntentClassifier not implemented yet")
def test_classify_with_history_includes_context_in_prompt():
    """
    히스토리가 있으면 프롬프트에 이전 대화 내용이 포함되어야 한다.
    
    User Story:
    "그거랑 비교해줘"처럼 대명사를 사용한 질문도 히스토리 기반으로 정확히 분류해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = '{"intent": "compare", "targets": ["claude", "gpt-4"], "reasoning": "Comparing with previously mentioned model"}'
    classifier = IntentClassifier(llm)
    
    query = "GPT-4랑 비교해줘"
    history = [
        {"role": "user", "content": "Claude에 대해 알려줘"},
        {"role": "assistant", "content": "Claude는 Anthropic이 만든 모델입니다."}
    ]
    
    # When
    result = classifier.classify(query, history)
    
    # Then
    llm.generate.assert_called_once()
    prompt = llm.generate.call_args[0][0]
    assert "Claude에 대해 알려줘" in prompt
    assert "GPT-4랑 비교해줘" in prompt
