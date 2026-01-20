import pytest
from unittest.mock import MagicMock
from app.domain.schemas.extraction import ExtractedMetadata
from app.domain.interfaces.llm import LLMInterface
from app.infrastructure.brain.adapter import LangGraphAdapter

class MockInnerLLM(LLMInterface):
    def extract_metadata(self, text: str) -> ExtractedMetadata | None:
        return ExtractedMetadata(
            title="Mock Title",
            summary="Mock Summary",
            keywords=["mock"],
            entities={},
            language="en"
        )

@pytest.mark.asyncio
async def test_langgraph_adapter_integration():
    """LangGraphAdapter가 그래프를 실행하고 결과를 올바르게 반환하는지 통합 테스트"""
    
    # 1. Prepare Inner LLM (that Nodes will use)
    mock_inner_llm = MockInnerLLM()
    
    # 2. Init Adapter
    adapter = LangGraphAdapter(llm=mock_inner_llm)
    
    # 3. Execute
    text = "This is a test content."
    # Note: Adapter methods might be sync or async depending on implementation.
    # Spec 006 protocols are sync. BUT LangGraph is async-native.
    # If the interface is Sync, we must block. If we updated interface to Async, await.
    # Current `LLMInterface` is sync.
    # However, `LangGraphAdapter.extract_metadata` will be implementing `LLMInterface`.
    # So it MUST be sync (`def extract_metadata`).
    # Internally it will call `graph.invoke` (sync) or `graph.ainvoke` (async).
    # `graph.invoke` is fine for now.
    
    result = adapter.extract_metadata(text)
    
    # 4. Verify
    assert result is not None
    assert isinstance(result, ExtractedMetadata)
    assert result.title == "Mock Title"
    
    # Verify State History (Optional, if we expose inspection)
    # adapter.graph should be accessible if we want to inspect
