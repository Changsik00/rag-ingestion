import pytest

from app.domain.interfaces.llm import LLMInterface
from app.domain.value_objects.extracted_metadata import ExtractedMetadata
from app.infrastructure.brain.adapter import LangGraphAdapter

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")



class MockInnerLLM(LLMInterface):
    async def extract_metadata(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
        return ExtractedMetadata(
            title="Mock Title", summary="Mock Summary", keywords=["mock"], entities={}, language="en"
        )

    def generate(self, prompt: str) -> str:
        return "mock"


@pytest.mark.asyncio
async def test_langgraph_adapter_integration():
    """LangGraphAdapter가 그래프를 실행하고 결과를 올바르게 반환하는지 통합 테스트"""

    # 1. Prepare Inner LLM (that Nodes will use)
    mock_inner_llm = MockInnerLLM()

    # 2. Init Adapter
    adapter = LangGraphAdapter(llm=mock_inner_llm)

    # 3. Execute
    text = "This is a test content."
    # Adapter methods are now async
    result = await adapter.extract_metadata(text)

    # 4. Verify
    assert result is not None
    assert isinstance(result, ExtractedMetadata)
    assert result.title == "Mock Title"

    # Verify State History (Optional, if we expose inspection)
    # adapter.graph should be accessible if we want to inspect
