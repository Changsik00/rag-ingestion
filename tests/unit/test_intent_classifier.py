import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.services.intent_classifier import IntentClassifier
from app.domain.schemas.intent import UserIntent, IntentType
from app.domain.interfaces.llm import LLMInterface

@pytest.fixture
def mock_llm():
    llm = MagicMock(spec=LLMInterface)
    llm.generate = AsyncMock()
    return llm

@pytest.fixture
def classifier(mock_llm):
    return IntentClassifier(llm=mock_llm)

@pytest.mark.asyncio
async def test_classify_detects_entities(classifier, mock_llm):
    # Given
    query = "일론 머스크와 트위터의 관계는?"
    history = []
    
    # Mock LLM response with new 'entities' field
    mock_llm.generate.return_value = """
    {
        "intent": "general_query",
        "targets": [],
        "entities": ["일론 머스크", "트위터"],
        "reasoning": "User asks about relationship between two entities"
    }
    """
    
    # When
    result = await classifier.classify(query, history)
    
    # Then
    assert getattr(result, "entities") == ["일론 머스크", "트위터"]
    assert result.intent == IntentType.GENERAL_QUERY
