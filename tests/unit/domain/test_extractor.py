import pytest
from unittest.mock import MagicMock
from app.domain.services.semantic_extractor import SemanticExtractor
from app.domain.schemas.extraction import ExtractedMetadata

def test_extract_success():
    # Setup
    mock_llm = MagicMock()
    
    # Instantiate extractor
    # Note: __init__ constructs the chain. We will replace the chain with a mock.
    extractor = SemanticExtractor(llm=mock_llm)
    
    # Prepare expected output
    expected_metadata = ExtractedMetadata(
        title="Test Title",
        summary="Test Summary",
        keywords=["k1", "k2"],
        entities={"Person": ["Tester"]}
    )
    
    # Mock the chain
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = expected_metadata
    extractor.chain = mock_chain
    
    # Execute
    result = extractor.extract("Dummy text")
    
    # Verify
    assert result is not None
    assert result.title == "Test Title"
    assert result.summary == "Test Summary"
    assert result.keywords == ["k1", "k2"]
    mock_chain.invoke.assert_called_once_with({"text": "Dummy text"})

def test_extract_failure():
    # Setup
    mock_llm = MagicMock()
    extractor = SemanticExtractor(llm=mock_llm)
    
    # Mock failure in chain
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("LLM Error")
    extractor.chain = mock_chain
    
    # Execute
    result = extractor.extract("Dummy text")
    
    # Verify
    # Should return None and log error
    assert result is None
