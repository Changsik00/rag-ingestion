import importlib
from unittest.mock import MagicMock

import pytest

from app.domain.interfaces.llm import LLMInterface


def test_graph_builder_import():
    if not importlib.util.find_spec("app.infrastructure.ai.ingestion_graph"):
        pytest.fail("app.infrastructure.ai.ingestion_graph module not found")

    try:
        from app.infrastructure.ai.ingestion_graph import IngestionGraphBuilder  # noqa: F401
    except ImportError:
        pytest.fail("IngestionGraphBuilder not found in app.infrastructure.ai.ingestion_graph")


def test_build_graph_returns_compiled_graph():
    """GraphBuilder가 컴파일된 그래프를 반환하는지 검증"""
    from app.infrastructure.ai.ingestion_graph import IngestionGraphBuilder

    mock_llm = MagicMock(spec=LLMInterface)
    builder = IngestionGraphBuilder(llm=mock_llm)

    graph = builder.build()

    # CompiledStateGraph인지 확인 (LangGraph 버전에 따라 타입 이름이 다를 수 있음, Runnable 여부 확인)
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "astream")

    # Check if it behaves like a CompiledGraph
    # Note: verify that the object returned is indeed runnable
    try:
        # Just compile check, execution needs valid state
        pass
    except Exception as e:
        pytest.fail(f"Graph build failed: {e}")
