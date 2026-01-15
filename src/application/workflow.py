from langgraph.graph import StateGraph, END
from src.domain.state import GraphState
from src.application.nodes.mock_nodes import fetch_source_node, extract_content_node

def create_workflow():
    """
    LangGraph Workflow를 생성하고 컴파일합니다.
    Flow: Fetch -> Extract -> END
    """
    # 1. Initialize StateGraph
    workflow = StateGraph(GraphState)
    
    # 2. Add Nodes
    workflow.add_node("fetch_source", fetch_source_node)
    workflow.add_node("extract_content", extract_content_node)
    
    # 3. Define Edges (Linear Flow)
    workflow.set_entry_point("fetch_source")
    workflow.add_edge("fetch_source", "extract_content")
    workflow.add_edge("extract_content", END)
    
    # 4. Compile
    app = workflow.compile()
    return app
