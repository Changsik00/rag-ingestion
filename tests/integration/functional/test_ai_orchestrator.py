import pytest

from app.application.services.orchestration.ingest import IngestOrchestrator
from app.domain.interfaces.llm import LLMInterface
from app.domain.value_objects.extracted_metadata import ExtractedMetadata

# pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


class MockInnerLLM(LLMInterface):
    async def aextract_metadata(self, text: str, thread_id: str | None = None) -> ExtractedMetadata | None:
        return ExtractedMetadata(
            title="Mock Title", summary="Mock Summary", keywords=["mock"], entities={}, language="en"
        )

    def generate(self, prompt: str) -> str:
        return "mock"


@pytest.mark.asyncio
async def test_langgraph_adapter_integration():
    """IngestionOrchestrator가 그래프를 실행하고 결과를 올바르게 반환하는지 통합 테스트"""

    # 1. Prepare Inner LLM (that Nodes will use)
    mock_inner_llm = MockInnerLLM()

    # 2. Init Adapter
    from app.infrastructure.ai.ingest.graph_builder import IngestionGraphBuilder
    builder = IngestionGraphBuilder(llm=mock_inner_llm)
    adapter = IngestOrchestrator(graph_builder=builder)

    # 3. Execute
    text = "This is a test content."
    # Adapter methods are now async
    result = await adapter.aextract_metadata(text)

    # 4. Verify
    assert result is not None
    assert isinstance(result, ExtractedMetadata)
    assert result.title == "Mock Title"

    # Verify State History (Optional, if we expose inspection)
    # adapter.graph should be accessible if we want to inspect
