# Implementation Plan: Spec-022 Human-in-the-loop

## 📋 Branch Strategy
- `feature/spec-022-human-in-the-loop`

## 🛑 User Review Required
- **In-Memory Checkpointer**: 현재는 DB(Postgres/Redis) 대신 `MemorySaver`를 사용하여 서버 재시작 시 상태가 휘발됩니다. (프로토타이핑 단계이므로 수용)

## 🎯 Core Strategy
1.  **MemorySaver 도입**: `langgraph.checkpoint.memory.MemorySaver`를 사용하여 그래프 상태를 메모리에 저장합니다.
2.  **Explicit Interrupt Node**: `human_review`라는 전용 노드를 만들고, Logic Resolver 진입 전 특정 조건(예: 이미 한 번 실패했거나, 신뢰도가 낮은 경우)에서 이 노드로 라우팅합니다.
3.  **Interrupt Config**: `compile(interrupt_before=["human_review"])` 설정을 통해 해당 노드 진입 직전에 실행을 멈춥니다.
4.  **Resumability**: `thread_id`를 사용하여 멈춘 지점의 상태를 조회하고(`get_state`), 필요한 경우 수정(`update_state`)한 뒤 실행을 재개(`stream/invoke`)합니다.

## 📂 Proposed Changes

### Component: Documentation (Design Guide)
#### [NEW] `docs/design_guides/human_in_the_loop_workflow.md`
- HITL(Human-in-the-loop)의 개념 설명 (Interrupt, Resume, State Update).
- 사용자가 개입 가능한 시나리오 및 선택지(수정, 승인, 포기) 정리.
- Mermaid 다이어그램을 통한 Workflow 시각화.

### Component: Brain (LangGraph)

#### [MODIFY] `app/infrastructure/brain/graph.py`
- `IngestionGraphBuilder`의 `__init__` 또는 `build` 메서드에 `checkpointer` 인자 추가.
- `human_review` 노드 등록.
- `validate_content` -> `human_review` (Conditional) 연결.
- `human_review` -> `resolve_logic` 연결.
- `compile` 시 `interrupt_before=["human_review"]` 설정.

```python
# graph.py snippet
def route_after_validation(state):
    # 실패했고 재시도 횟수가 남았으면 Logic Resolver로 가는데,
    # 만약 "중대한 오류"라면 human_review를 거치도록 설정 가능
    if state.get("error"):
        return "human_review" 
    return END

workflow.add_conditional_edges("validate_content", route_after_validation, ...)
workflow.compile(checkpointer=checkpointer, interrupt_before=["human_review"])
```

#### [MODIFY] `app/infrastructure/brain/nodes.py`
- `human_review` 메서드 추가 (Pass-through).

```python
def human_review(self, state: IngestionState) -> IngestionState:
    # 사용자가 개입하는 시점.
    # 실제로 수행할 작업은 없으며, 여기서 멈추는 것이 목적이므로 상태 그대로 반환.
    return state
```

### Component: Tests

#### [NEW] `tests/integration/test_human_loop.py`
- `MemorySaver`를 사용하는 통합 테스트 작성.
- 시나리오:
    1. 그래프 실행 -> `human_review`에서 중단 확인.
    2. 상태 조회 (`get_state`) -> 현재 상태 검증.
    3. 상태 수정 (`update_state`) -> metadata 수정 등.
    4. 실행 재개 (`stream(None)`) -> 수정된 상태로 Logic Resolver 진행 확인.

## 🧪 Verification Plan

### Automated Tests
```bash
# 새로운 HITL 통합 테스트 실행
uv run pytest tests/integration/test_human_loop.py -v

# Lint Check
uv run ruff check . --fix
```

### Manual Verification
- (현재 Admin UI가 LangGraph State와 연동되지 않았으므로, 단위/통합 테스트로 검증하는 것이 주효함)
