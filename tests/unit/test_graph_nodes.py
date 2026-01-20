import pytest
from unittest.mock import MagicMock
from app.domain.ingestion.state import IngestionState
from app.domain.interfaces.llm import LLMInterface
from app.domain.schemas.extraction import ExtractedMetadata

def test_nodes_module_import():
    try:
        from app.infrastructure.brain.nodes import IngestionNodes
    except ImportError:
        pytest.fail("IngestionNodes class not found in app.infrastructure.brain.nodes")

def test_nodes_initialization():
    """IngestionNodes 클래스가 LLMInterface를 주입받아 초기화되는지 검증"""
    from app.infrastructure.brain.nodes import IngestionNodes
    mock_llm = MagicMock(spec=LLMInterface)
    nodes = IngestionNodes(llm=mock_llm)
    assert nodes.llm == mock_llm

def test_extract_metadata_node():
    """extract_metadata 노드가 LLM을 호출하고 State를 갱신하는지 검증"""
    from app.infrastructure.brain.nodes import IngestionNodes
    
    # Mock LLM & Result
    mock_llm = MagicMock(spec=LLMInterface)
    mock_metadata = ExtractedMetadata(
        title="Test Title",
        summary="Test Summary",
        keywords=["test"],
        entities={},
        language="en"
    )
    mock_llm.extract_metadata.side_effect = lambda x: mock_metadata 
    
    nodes = IngestionNodes(llm=mock_llm)
    
    state: IngestionState = {
        "original_url": "http://test.com",
        "raw_content": "test content",
        "metadata": {},
        "extracted_entities": [],
        "steps_history": [],
        "error": None,
        "retry_count": 0
    }
    
    # Execute Node (Sync)
    result = nodes.extract_metadata(state)
    
    # Verify State Update
    assert "metadata" in result
    # Pydantic model dump check
    assert result["metadata"]["title"] == "Test Title"
    
    # Determine if steps_history is updated
    assert "steps_history" in result
    assert "extract_metadata" in result["steps_history"]

def test_validate_content_node():
    """validate_content 노드 존재 여부 확인"""
    from app.infrastructure.brain.nodes import IngestionNodes
    mock_llm = MagicMock(spec=LLMInterface)
    nodes = IngestionNodes(llm=mock_llm)
    assert hasattr(nodes, 'validate_content')
