import pytest
from unittest.mock import Mock
from app.domain.interfaces.llm import LLMInterface
# The service module does not exist yet; this import is expected to fail initially.
try:
    from app.domain.services.query_rewriter import QueryRewriter
except ImportError:
    QueryRewriter = None

@pytest.mark.skipif(QueryRewriter is None, reason="QueryRewriter not implemented yet")
def test_rewrite_with_empty_history_returns_original():
    """
    히스토리가 비어있으면 LLM 호출 비용 없이 원본 쿼리를 즉시 반환해야 한다.
    (Non-functional Optimization Requirement)
    """
    # Given
    llm = Mock(spec=LLMInterface)
    rewriter = QueryRewriter(llm)
    query = "일론 머스크는 누구야?"
    history = []

    # When
    result = rewriter.rewrite(query, history)

    # Then
    assert result == query
    llm.generate.assert_not_called()

@pytest.mark.skipif(QueryRewriter is None, reason="QueryRewriter not implemented yet")
def test_rewrite_with_history_calls_llm():
    """
    히스토리가 있으면 LLM을 호출하여 쿼리를 재구성해야 한다.
    """
    # Given
    llm = Mock(spec=LLMInterface)
    llm.generate.return_value = "일론 머스크의 형제는 누구입니까?"
    rewriter = QueryRewriter(llm)
    
    query = "그의 형제는?"
    history = [
        {"role": "user", "content": "일론 머스크에 대해 알려줘"},
        {"role": "assistant", "content": "일론 머스크는 테슬라의 CEO입니다."}
    ]

    # When
    result = rewriter.rewrite(query, history)

    # Then
    assert result == "일론 머스크의 형제는 누구입니까?"
    llm.generate.assert_called_once()
    
    # Prompt verification
    prompt_sent = llm.generate.call_args[0][0]
    assert "일론 머스크에 대해 알려줘" in prompt_sent
    assert "그의 형제는?" in prompt_sent
