from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.domain.ingestion.state import IngestionGraphState
from app.domain.interfaces.llm import LLMInterface
from app.infrastructure.ai.nodes.ingestion_nodes import IngestionNodes


class IngestionGraphBuilder:
    """
    Ingestion Pipeline의 StateGraph를 구성하고 컴파일하는 빌더 클래스.
    Clean Architecture의 Infrastructure 레이어에 속하며,
    Domain의 Interface(LLM)와 State 정의를 사용하여 실제 실행 가능한 그래프를 생성합니다.
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.nodes = IngestionNodes(llm)

    def build(self, checkpointer: Any = None) -> CompiledStateGraph:
        """
        Ingestion Workflow 그래프를 생성하고 컴파일하여 반환합니다.

        Args:
            checkpointer (Any, optional): LangGraph Checkpointer (MemorySaver etc). Defaults to None.
        """
        # 1. StateGraph 생성
        workflow = StateGraph(IngestionGraphState)

        # 2. Node 추가
        workflow.add_node("extract_metadata", self.nodes.extract_metadata)
        workflow.add_node("validate_content", self.nodes.validate_content)
        workflow.add_node("resolve_logic", self.nodes.resolve_logic)
        workflow.add_node("analyze_failure", self.nodes.analyze_failure)  # Spec 023
        workflow.add_node("human_review", self.nodes.human_review)

        # 3. Edge 연결
        # Flow: Extract -> Validate -> Logic (Conditional) or Human Review -> Extract or End

        workflow.set_entry_point("extract_metadata")
        workflow.add_edge("extract_metadata", "validate_content")

        # Conditional Edge Logic
        def route_after_validation(state: IngestionGraphState):
            # 0. Check Forced HITL (Feature Flag)
            if state.get("hitl_enabled"):
                return "human_review"

            # If validation passed (no error), End.
            # If validation failed, go to logic resolver.

            # TODO: Actual Validator should clear error if passed.
            if state.get("error") or state.get("last_feedback"):
                if state.get("retry_count", 0) >= state.get("max_retries", 3):
                    # 재시도 횟수 초과 시 Human Review (또는 바로 종료)
                    # 여기서는 중요 에러나 한계 도달 시 Human Review로 보낸다고 가정
                    return "human_review"

                # 일반적인 에러는 Logic Resolver로 가기 전에 Failure Analysis를 거침
                # 단, 'Critical Error' 메시지가 있으면 바로 Human Review로 보낼 수도 있음
                if "Critical" in str(state.get("error", "")):
                    return "human_review"

                return "analyze_failure"

            return END

        workflow.add_conditional_edges(
            "validate_content",
            route_after_validation,
            {
                "resolve_logic": "resolve_logic",  # This might not be needed in map if not returned
                "analyze_failure": "analyze_failure",
                "human_review": "human_review",
                END: END,
            },
        )

        # Logic Resolver always loops back to Extraction (Backtracking)
        workflow.add_edge("analyze_failure", "resolve_logic")
        workflow.add_edge("resolve_logic", "extract_metadata")

        # Human Review -> Logic Resolver (수정 사항 반영 후 전략 재수립)
        workflow.add_edge("human_review", "resolve_logic")

        # 4. Compile
        # interrupt_before=["human_review"] 설정을 통해 해당 노드 진입 전 멈춤
        if checkpointer:
            return workflow.compile(checkpointer=checkpointer, interrupt_before=["human_review"])

        return workflow.compile()
