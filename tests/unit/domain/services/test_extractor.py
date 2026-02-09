from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.interfaces.llm_interface import LLMInterface
from app.application.services.semantic_extractor import SemanticExtractor
from app.domain.value_objects.extracted_metadata import ExtractedMetadata
from app.domain.value_objects.ontology import EntityType


@pytest.mark.asyncio
async def test_extract_success():
    """SemanticExtractor가 LLM interface(async)를 통해 메타데이터를 성공적으로 추출하는지 테스트"""
    # Setup: Protocol Mock
    mock_llm = MagicMock(spec=LLMInterface)
    expected_metadata = ExtractedMetadata(
        title="AI Research and Development Practices",
        summary="Comprehensive guide on modern AI development",
        keywords=["AI", "Research", "Development"],
        entities={
            EntityType.PERSON: ["Geoffrey Hinton", "Yann LeCun"],
            EntityType.ORGANIZATION: ["Google DeepMind", "Meta AI"],
            EntityType.TECHNOLOGY: ["Python", "PyTorch", "TensorFlow"],
            EntityType.CONCEPT: ["Deep Learning", "Neural Networks"],
            EntityType.LOCATION: ["Silicon Valley", "Montreal"],
            EntityType.EVENT: ["NeurIPS 2024"],
            EntityType.ACTIVITY: ["벤치마킹", "모델 학습", "데이터 전처리"],
        },
    )
    # Adapter methods are now async
    mock_llm.aextract_metadata = AsyncMock(return_value=expected_metadata)

    # Execute
    extractor = SemanticExtractor(llm=mock_llm)
    result = await extractor.extract("Dummy text")

    # Verify
    assert result is not None
    assert result.title == "AI Research and Development Practices"
    assert result.summary == "Comprehensive guide on modern AI development"
    assert result.keywords == ["AI", "Research", "Development"]
    assert result.entities[EntityType.PERSON] == ["Geoffrey Hinton", "Yann LeCun"]
    assert result.entities[EntityType.ACTIVITY] == ["벤치마킹", "모델 학습", "데이터 전처리"]
    mock_llm.aextract_metadata.assert_called_once_with("Dummy text", metadata=None, thread_id=None)


@pytest.mark.asyncio
async def test_extract_failure():
    """LLM 추출 실패 시 None을 반환하는지 테스트"""
    # Setup
    mock_llm = MagicMock(spec=LLMInterface)
    mock_llm.aextract_metadata = AsyncMock(return_value=None)

    # Execute
    extractor = SemanticExtractor(llm=mock_llm)
    result = await extractor.extract("Dummy text")

    # Verify
    assert result is None
    mock_llm.aextract_metadata.assert_called_once_with("Dummy text", metadata=None, thread_id=None)
