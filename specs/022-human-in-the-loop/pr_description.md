# feat(spec-022): human-in-the-loop checkpointer

## 📋 Summary
LLM 인제스션 파이프라인에서 신뢰도가 낮거나 시스템이 스스로 해결할 수 없는 문제 발생 시, 실행을 멈추고(**Interrupt**) 사용자의 검토를 요청하는 **Human-in-the-loop (HITL)** 메커니즘을 도입했습니다.

`LangGraph`의 `Checkpointer`와 `interrupt_before` 기능을 활용하여 `human_review` 노드에서 대기 상태를 유지하며, 사용자가 상태를 수정(`update_state`)한 후 재개(`resume`)할 수 있습니다.

## 🎯 Key Review Points
1.  **IngestionGraphBuilder (`graph.py`)**:
    - `checkpointer` 파라미터가 `build()` 메서드에 추가되었습니다.
    - `human_review` 노드가 추가되었으며, `validate_content` 실패 시 중요도에 따라 이 노드로 라우팅됩니다.
    - `interrupt_before=["human_review"]` 설정이 적용되었습니다.

2.  **IngestionNodes (`nodes.py`)**:
    - `human_review` 메서드가 추가되었습니다 (Pass-through).

3.  **Tests**:
    - `tests/integration/bdd/test_human_loop.py`에서 Interrupt -> State Update -> Resume 전체 흐름을 검증합니다.

4.  **Docs**:
    - `docs/design_guides/human_in_the_loop_workflow.md`: HITL 개념 및 제어 가이드가 추가되었습니다.

## 🧪 Verification
### Automated Tests
```bash
# Spec 022 전용 통합 테스트
uv run pytest tests/integration/bdd/test_human_loop.py -v

# 전체 테스트 슈트
uv run pytest
```

## 📦 Files Changed

### 🆕 New Files
- `docs/design_guides/human_in_the_loop_workflow.md`: HITL 디자인 가이드
- `tests/integration/bdd/test_human_loop.py`: HITL 통합 테스트
- `specs/022-human-in-the-loop/`: Spec 문서 (Spec, Plan, Task)

### 🛠 Modified Files
- `app/infrastructure/brain/graph.py`: Graph 빌더에 HITL 설정 추가
- `app/infrastructure/brain/nodes.py`: `human_review` 노드 추가
- `backlog/queue.md`: Future Works (Persistence, Notification) 추가
