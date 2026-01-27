feat(spec-041): admin hitl ui and robustness

## Summary
Spec 040(Verification Script)에서 발견된 Admin Dashboard의 사용성 문제와 Checkpointer 충돌 가능성을 해결하고, 잘못된 번호링(Spec 040 vs 041)으로 인한 충돌을 복구했습니다.
HITL 모드에서 사용자가 작업을 명시적으로 승인하고 재개할 수 있는 UI와 백엔드 로직을 구현했습니다.

## Changes
- **Branch Rename**: `feature/spec-040-hitl-script` -> `feature/spec-041-hitl-ui-robustness`
- **Frontend (Streamlit)**: 
  - `4_RAG_Playground.py`: Resume/Approve 버튼 및 대기 상태 표시기 구현.
- **Backend**: 
  - `adapter.py` & `endpoints/rag.py`: 비동기 상태 갱신 및 재개 로직 안정화.
- **Docs**: 
  - `specs/041-hitl-ui-robustness/`: Spec/Plan/Task 문서 복구.
  - `docs/architecture/hitl_and_persistence.md`: 아키텍처 가이드 추가.

## Key Review Points
- **Architecture**: `rag-{uuid}` 네임스페이스 전략이 다중 사용자 환경에서 충돌을 방지하는지.
- **UX**: 승인 버튼 클릭 시 대화가 매끄럽게 이어지는지.
- **Recovery**: Spec 040과 041의 역할 분리가 명확한지.

## Issue
- Resolves Spec 041 (Backlog)
- Fixes Spec 040 Collision
