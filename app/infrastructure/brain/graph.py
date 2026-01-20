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
        workflow.add_node("extract_metadata", self.nodes.extract_metadata)
        workflow.add_node("validate_content", self.nodes.validate_content)
        workflow.add_node("resolve_logic", self.nodes.resolve_logic)  # New Node

        # 3. Edge 연결
        # Flow: Extract -> Validate -> Logic (Conditional) -> Extract or End

        workflow.set_entry_point("extract_metadata")
        workflow.add_edge("extract_metadata", "validate_content")

        # Conditional Edge Logic
        def route_after_validation(state: IngestionState):
            # If validation passed (no error), End.
            # If validation failed, go to logic resolver.

            # TODO: Actual Validator should clear error if passed.
            if state.get("error") or state.get("last_feedback"):
                if state.get("retry_count", 0) >= state.get("max_retries", 3):
                    return END
                return "resolve_logic"

            return END

        workflow.add_conditional_edges(
            "validate_content",
            route_after_validation,
            {
                "resolve_logic": "resolve_logic",
                END: END
            }
        )

        # Logic Resolver always loops back to Extraction (Backtracking)
        workflow.add_edge("resolve_logic", "extract_metadata")

        # 4. Compile
        return workflow.compile()
