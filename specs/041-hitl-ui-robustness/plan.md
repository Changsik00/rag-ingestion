# Plan 041: Admin HITL UI & Robustness

## 1. Strategy
이미 기능 구현은 대부분 완료된 상태(Recovery)이므로, 기존 코드를 정리하고 문서화를 보강하는 방향으로 진행한다.
Key Focus: Streamlit UI의 사용자 경험(UX) 개선과 Checkpointer 안정성 확보.

## 2. Changes
### 2.1 Admin Dashboard (Streamlit)
- `app/interfaces/streamlit/pages/4_RAG_Playground.py`:
    - `st.button("승인 및 계속")` 추가.
    - Session State를 활용하여 중복 클릭 방지.
    - Interrupt 상태 감지 로직 개선.

### 2.2 Backend (FastAPI & LangGraph)
- `app/infrastructure/brain/adapter.py`:
    - `update_state` 메소드가 비동기 환경에서 안전하게 동작하도록 수정.
- `app/interfaces/api/endpoints/rag.py`:
    - `/resume` 엔드포인트가 올바른 `thread_id`와 `checkpoint_id`를 참조하도록 검증 로직 추가.

### 2.3 Documentation
- `docs/architecture/hitl_and_persistence.md`: 신규 작성.

## 3. Verification Plan
### 3.1 Manual Verification
- **Scenario**: 질문 -> LLM 답변(Wait) -> "승인" 버튼 클릭 -> "감사합니다" 등의 후속 답변 확인.
- **Check**: 버튼 클릭 시 에러 없이 부드럽게 이어지는지, DB(SQLite)에 체크포인트가 정상 갱신되는지 확인.
