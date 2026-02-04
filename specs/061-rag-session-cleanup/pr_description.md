feat(spec-061): manual session cleanup and admin ui improvement

## 📝 Summary
Spec-061: RAG 세션 데이터의 확실한 삭제를 위한 Backend 로직 개선 및 Admin UI 접근성 향상.

## 🛠 Key Changes
- **Backend (`rag.py`)**: `reset_session` 호출 시 Checkpointer가 삭제 기능을 미지원할 경우, Fallback으로 직접 SQL(`DELETE`)을 수행하여 `checkpoints`, `writes` 등을 정리하도록 개선.
- **Frontend (`4_RAG_Playground.py`)**: "New Chat" 및 "Delete History" 버튼을 "Advanced Settings"에서 **Sidebar** 최상단으로 이동.
- **Tests**: `tests/integration/functional/test_rag_session_cleanup.py` 추가 (TDD Verification).

## 💡 Review Points
- `reset_session`의 SQL Delete 쿼리가 LangGraph Postgres 스키마(`checkpoints`, `checkpoint_writes` 등)와 일치하는지 확인.
- Admin UI 사이드바 버튼 동작 테스트 권장.

## ✅ Checklist
- [x] Spec 061 요구사항 충족
- [x] 통합 테스트 Pass
- [x] Ruff Lint/Format Pass
