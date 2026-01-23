"""
RAG Pipeline의 StateGraph를 구성하고 컴파일하는 빌더 클래스.

Ingestion Pipeline의 IngestionGraphBuilder 패턴을 재사용하여
RAG 전용 Linear Pipeline을 구성합니다.

Spec 033: LangGraph State Management
"""

from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.domain.rag.state import RAGGraphState
from app.infrastructure.rag.nodes import RAGNodes


class RAGGraphBuilder:
    """
    RAG Pipeline의 StateGraph를 구성하고 컴파일하는 빌더 클래스.
    
    4-Node Linear Pipeline을 구성합니다:
    1. classify_intent: Intent Classification + Query Rewriting
    2. route_decision: Intent → Filters 변환
    3. retrieve_hybrid: Parallel Hybrid Search
    4. generate_answer: LLM Answer Generation
    """

    def __init__(self, nodes: RAGNodes):
        """
        Args:
            nodes: RAG Nodes 비즈니스 로직 클래스
        """
        self.nodes = nodes

    def build(self, checkpointer: Any = None) -> CompiledStateGraph:
        """
        RAG Workflow 그래프를 생성하고 컴파일하여 반환합니다.
        
        Args:
            checkpointer: LangGraph Checkpointer (SqliteSaver 등). Defaults to None.
            
        Returns:
            CompiledStateGraph: 실행 가능한 RAG Graph
        """
        # 1. StateGraph 생성
        workflow = StateGraph(RAGGraphState)

        # 2. Node 추가
        workflow.add_node("classify_intent", self.nodes.classify_intent)
        workflow.add_node("route_decision", self.nodes.route_decision)
        workflow.add_node("retrieve_hybrid", self.nodes.retrieve_hybrid)
        workflow.add_node("generate_answer", self.nodes.generate_answer)

        # 3. Edge 연결 (Linear Pipeline)
        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "route_decision")
        workflow.add_edge("route_decision", "retrieve_hybrid")
        workflow.add_edge("retrieve_hybrid", "generate_answer")
        workflow.add_edge("generate_answer", END)

        # 4. Compile
        # Checkpointer가 제공되면 State Snapshot 저장 기능 활성화
        if checkpointer:
            return workflow.compile(checkpointer=checkpointer)
        return workflow.compile()
