from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.domain.ingestion.state import IngestionState
from app.domain.interfaces.llm import LLMInterface
from app.infrastructure.brain.nodes import IngestionNodes


class IngestionGraphBuilder:
    """
    Ingestion Pipeline의 StateGraph를 구성하고 컴파일하는 빌더 클래스.
    Clean Architecture의 Infrastructure 레이어에 속하며,
    Domain의 Interface(LLM)와 State 정의를 사용하여 실제 실행 가능한 그래프를 생성합니다.
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.nodes = IngestionNodes(llm)

    def build(self) -> CompiledStateGraph:
        """
        Ingestion Workflow 그래프를 생성하고 컴파일하여 반환합니다.

        Returns:
            CompiledStateGraph: 실행 가능한 LangGraph 객체 (Runnable)
        """
        # 1. StateGraph 생성
        workflow = StateGraph(IngestionState)

        # 2. Node 추가
        # 각 노드는 IngestionNodes의 메서드로 정의됨
        workflow.add_node("extract_metadata", self.nodes.extract_metadata)
        workflow.add_node("validate_content", self.nodes.validate_content)

        # 3. Edge 연결 (Linear Flow for Phase 1 Migration)
        # Entry -> Extract -> Validate -> End
        workflow.set_entry_point("extract_metadata")
        workflow.add_edge("extract_metadata", "validate_content")
        workflow.add_edge("validate_content", END)

        # 4. Compile
        return workflow.compile()
