import pytest
from langgraph.graph import StateGraph
from src.application.workflow import create_workflow

def test_workflow_compilation():
    """Workflow가 정상적으로 생성되고 컴파일되는지 검증"""
    try:
        app = create_workflow()
        
        # 컴파일된 그래프 객체 검증
        assert app is not None
        # LangGraph 내부 구조 확인 (노드 존재 여부)
        # compiled graph 'app' doesn't expose nodes directly easily in public API,
        # but successful compilation implies structure is valid.
        
        # Test basic invocation with mock nodes
        result = app.invoke({"urls": ["https://test-workflow.com"]})
        
        # Assertions
        assert result["status"] == "extracted"
        assert len(result["sources"]) == 1
        assert str(result["sources"][0].url) == "https://test-workflow.com/"
        assert len(result["sources"][0].chunks) > 0

    except Exception as e:
        pytest.fail(f"Workflow compilation or execution failed: {e}")
