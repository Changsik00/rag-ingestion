from unittest.mock import AsyncMock

import pytest

from app.domain.ingestion.state import IngestionState, ValidationFeedback
from app.infrastructure.ai.graphs.ingestion_graph import IngestionGraphBuilder

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")



@pytest.fixture
def mock_llm():
    """
    AsyncMock을 사용하여 이벤트 루프 에러를 방지하고
    비동기 메서드 호출을 시뮬레이션합니다.
    """
    llm = AsyncMock()
    # extract_metadata 호출 시 반환될 기본값 설정
    llm.extract_metadata.return_value = {"title": "Test Title", "summary": "Test Summary"}
    return llm


@pytest.mark.asyncio
async def test_reasoning_flow_integration(mock_llm):
    """
    Given: Validation이 실패하여 재시도가 필요한 상황
    When: Graph가 실행되면
    Then:
        1. validate_content (Fail) -> analyze_failure (Run) -> resolve_logic 순으로 실행된다.
        2. analyze_failure 노드가 실행되어 State에 FailureHypothesis가 생성된다.
    """
    # 1. Graph Builder 초기화
    builder = IngestionGraphBuilder(mock_llm)
    nodes = builder.nodes

    # 2. validate_content 노드를 몽키패치하여 실패 시나리오 구성
    original_validate = nodes.validate_content

    async def failing_validate(state: IngestionState):
        current_history = state.get("steps_history", [])

        # analyze_failure가 이미 실행되었다면, 루프를 종료하기 위해 성공으로 간주
        if "analyze_failure" in current_history:
            return {"steps_history": current_history + ["validate_content"], "error": None, "last_feedback": None}

        # 첫 호출 시 실패 발생
        return {
            "error": "Simulated Validation Error",
            "last_feedback": ValidationFeedback(source="validator", message="Field missing", target_fields=["summary"]),
            "steps_history": current_history + ["validate_content"],
        }

    # 노드 교체 (Async 호환을 위해 비동기 함수로 패치)
    nodes.validate_content = failing_validate

    # 3. Graph 빌드
    app = builder.build()

    # 4. 초기 State 설정
    input_state = IngestionState(
        original_url="http://test.com",
        raw_content="content",
        metadata=None,
        steps_history=[],
        error=None,
        retry_count=0,
        max_retries=1,
        current_strategy="STANDARD",
        active_constraints={},
        attempt_history=[],
        last_feedback=None,
        predicted_category=None,
        backtracking_context=None,
    )

    # 5. Graph 실행 (비동기 호출)
    final_state = await app.ainvoke(input_state)

    # 6. 검증 (Assertion)
    history = final_state["steps_history"]

    # 순서 보장 확인 (최소한 포함 여부 확인)
    assert "extract_metadata" in history
    assert "validate_content" in history
    assert "analyze_failure" in history  # 이 테스트의 핵심 목적

    # 실패 가설(Failure Hypothesis)이 생성되었는지 확인
    context = final_state.get("backtracking_context")
    assert context is not None
    # 이 부분은 analyze_failure 노드의 실제 로직에 따라 필드명을 맞춰주세요.
    assert "failure_hypothesis" in context

    # 7. 원복 (Clean up)
    nodes.validate_content = original_validate
