# Walkthrough: Spec-022 Human-in-the-loop

## 1. 개요
이 문서는 **Spec 022: Human-in-the-loop Checkpointer** 작업의 구현 과정과 검증 결과를 기록한 문서입니다. `LangGraph`의 `MemorySaver`를 활용하여 실행 중단(Interrupt) 및 재개(Resume) 흐름을 구현했습니다.

## 2. 변경 사항
### 2.1 Graph Architecture Checkpointer
- `IngestionGraphBuilder`에 `checkpointer` 인자가 추가되었습니다.
- Conditional Edge에서 Critical Error 발생 시 `human_review` 노드로 이동하도록 라우팅을 수정했습니다.
- `human_review` 노드 진입 전 `interrupt_before`가 트리거됩니다.

### 2.2 Human Review Node
- `IngestionNodes.human_review`: 상태를 그대로 유지하며 멈추는 Passthrough 노드입니다.

## 3. 검증 결과 (Verification)
### 3.1 Integration Test (`test_human_loop.py`)
> **시나리오**: Validation Error 발생 -> Interrupt -> User가 Error Clear -> Resume -> 정상 완료

* **결과**: **PASS**
* **로그 요약**:
```
--- Starting Graph Execution ---
Event: {'extract_metadata': ...}
--- Snapshot at Interrupt: ('human_review',) ---
--- User Updating State ---
--- Resuming Graph ---
Resume Event: {'extract_metadata': ...}
```
* **Linting**: `ruff check . --fix` 통과 완료.

## 4. Known Issues / Future Works
- **Persistence**: 현재는 In-Memory(`MemorySaver`) 방식이므로 서버 재시작 시 상태가 유실됩니다. 추후 DB(`PostgresSaver`) 연동이 필요합니다.
- **Admin UI**: 사용자가 개입할 수 있는 UI가 아직 구현되지 않았습니다 (API로만 가능).
