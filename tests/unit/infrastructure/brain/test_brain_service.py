from unittest.mock import AsyncMock

import pytest

from app.domain.services.intent_classifier import IntentClassifier
from app.domain.services.query_rewriter import QueryRewriter
from app.domain.value_objects.intent import IntentType, UserIntent
from app.infrastructure.brain.service import BrainService


@pytest.fixture
def mock_intent_classifier():
    return AsyncMock(spec=IntentClassifier)


@pytest.fixture
def mock_query_rewriter():
    return AsyncMock(spec=QueryRewriter)


@pytest.fixture
def brain_service(mock_intent_classifier, mock_query_rewriter):
    return BrainService(mock_intent_classifier, mock_query_rewriter)


@pytest.mark.asyncio
async def test_classify_and_rewrite_success(brain_service, mock_intent_classifier, mock_query_rewriter):
    # Given
    query = "test query"
    history = []
    expected_intent = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="test")
    mock_intent_classifier.classify.return_value = expected_intent
    mock_query_rewriter.rewrite.return_value = "rewritten query"

    # When
    result_intent, result_query = await brain_service.classify_and_rewrite(query, history)

    # Then
    assert result_intent == expected_intent
    assert result_query == "rewritten query"
    mock_intent_classifier.classify.assert_awaited_once_with(query, history)
    mock_query_rewriter.rewrite.assert_awaited_once_with(query, history)


@pytest.mark.asyncio
async def test_classify_and_rewrite_intent_failure_fallback(brain_service, mock_intent_classifier, mock_query_rewriter):
    # Given
    query = "test query"
    history = []

    # Mock IntentClassifier to raise exception
    mock_intent_classifier.classify.side_effect = Exception("Intent error")
    mock_query_rewriter.rewrite.return_value = "rewritten query"

    # When
    result_intent, result_query = await brain_service.classify_and_rewrite(query, history)

    # Then
    assert result_intent.intent == IntentType.GENERAL_QUERY
    assert "Fallback" in result_intent.reasoning
    assert result_query == "rewritten query"


@pytest.mark.asyncio
async def test_classify_and_rewrite_rewrite_failure_fallback(
    brain_service, mock_intent_classifier, mock_query_rewriter
):
    # Given
    query = "test query"
    history = []
    expected_intent = UserIntent(intent=IntentType.GENERAL_QUERY, targets=[], reasoning="test")
    mock_intent_classifier.classify.return_value = expected_intent

    # Mock QueryRewriter to raise exception (even though implementation swallows it,
    # BrainService has extra safeguard we want to test)
    mock_query_rewriter.rewrite.side_effect = Exception("Rewrite error")

    # When
    result_intent, result_query = await brain_service.classify_and_rewrite(query, history)

    # Then
    assert result_intent == expected_intent
    assert result_query == query  # Should return original query
