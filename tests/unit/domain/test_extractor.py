import pytest
from unittest.mock import MagicMock
from app.domain.services.semantic_extractor import SemanticExtractor
from app.domain.schemas.extraction import ExtractedMetadata
from app.domain.interfaces.llm import LLMInterface


def test_extract_success():
    """SemanticExtractor가 LLM interface를 통해 메타데이터를 성공적으로 추출하는지 테스트"""
    # Setup: Protocol Mock
    mock_llm = MagicMock(spec=LLMInterface)
    expected_metadata = ExtractedMetadata(
        title="Test Title",
        summary="Test Summary",
        keywords=["k1", "k2"],
        entities={"Person": ["Tester"]}
    )
    mock_llm.extract_metadata.return_value = expected_metadata
    
    # Execute
    extractor = SemanticExtractor(llm=mock_llm)
    result = extractor.extract("Dummy text")
    
    # Verify
    assert result is not None
    assert result.title == "Test Title"
    assert result.summary == "Test Summary"
    assert result.keywords == ["k1", "k2"]
    assert result.entities == {"Person": ["Tester"]}
    mock_llm.extract_metadata.assert_called_once_with("Dummy text")


def test_extract_failure():
    """LLM 추출 실패 시 None을 반환하는지 테스트"""
    # Setup
    mock_llm = MagicMock(spec=LLMInterface)
    mock_llm.extract_metadata.return_value = None
    
    # Execute
    extractor = SemanticExtractor(llm=mock_llm)
    result = extractor.extract("Dummy text")
    
    # Verify
    assert result is None
    mock_llm.extract_metadata.assert_called_once_with("Dummy text")
