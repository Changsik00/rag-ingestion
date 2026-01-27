# Task List: Spec 041 - Admin HITL UI & Robustness

## Progress
- [x] Spec 번호 확정 (040 -> 041)
- [x] spec.md 작성 (Reverse Engineering)
- [x] plan.md 작성 (Reverse Engineering)
- [x] task.md 작성 (Reverse Engineering)
- [x] 백로그 업데이트
- [x] User Plan Accept
- [x] Feature 브랜치 리네임: `feature/spec-041-hitl-ui-robustness`

---

## Task 1: HITL UI Implementation (Recovered)

### 1-1. Resume/Approve UI
- [x] `app/interfaces/streamlit/pages/4_RAG_Playground.py`: Resume/Approve 버튼 구현
- [x] `app/interfaces/streamlit/pages/4_RAG_Playground.py`: "검토 대기 중" 상태 표시기 구현
- [x] `app/interfaces/streamlit/pages/4_RAG_Playground.py`: 중복 메시지 방지 로직

### 1-2. Backend & State Management
- [x] `app/infrastructure/brain/adapter.py`: `update_state` 로직 수정
- [x] `app/interfaces/api/endpoints/rag.py`: Resume API 워크플로우 호출 수정

### 1-3. Documentation
- [x] `docs/architecture/hitl_and_persistence.md`: HITL 아키텍처 문서 추가

---

## Task 2: Completion & Merge

### 2-1. Final Check
- [ ] Code Quality Check (`ruff check`)
- [ ] Manual Verification (Playground)

### 2-2. PR Creation
- [ ] Walkthrough 작성
- [ ] PR Description 작성
- [ ] Create PR: `feat(spec-041): admin hitl ui and robustness`
