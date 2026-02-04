# Implementation Plan: Spec-061

## 📋 Branch Strategy
- `feature/spec-061-rag-session-cleanup`

## 🛑 User Review Required
> [!NOTE]
> - `AsyncPostgresSaver` 라이브러리 내부 구조에 의존하지 않고, 직접 SQL `DELETE` 쿼리를 실행하여 데이터를 정리합니다. 이는 라이브러리 스키마 변경 시 수정이 필요할 수 있습니다.

## 🎯 Core Strategy

### Architecture Context
- **Backend Integration**: `AsyncPostgresSaver`는 표준 `adelete` 인터페이스가 부족하므로, `app/interfaces/api/v1/endpoints/rag.py` 내부 또는 별도 Service 함수에서 직접 `pool.connection()`을 사용하여 삭제 쿼리를 실행합니다.
- **UI UX**: Streamlit `st.sidebar`를 활용하여 주요 액션 버튼을 상시 노출합니다.

## 📂 Proposed Changes

### [Backend] API Layer

#### [MODIFY] `app/interfaces/api/v1/endpoints/rag.py`
- `reset_session` 함수 수정:
  - `checkpointer` 객체 확인.
  - `adelete_thread`가 없으면, `database.pool`을 이용해 직접 SQL 실행.
  - Target Tables: `checkpoints`, `checkpoint_blobs`, `checkpoint_writes`.

### [Frontend] Admin UI

#### [MODIFY] `admin/pages/4_RAG_Playground.py`
- "Advanced Settings" 내의 버튼 제거.
- `st.sidebar` 상단에 "New Chat", "Delete History" 버튼 배치.
- Session State 관리 로직 단순화.

## 🧪 Verification Plan

### Automated Tests
```bash
# Integration Test for Reset API
uv run pytest tests/integration/test_rag_api.py -k "test_reset_session"
```
*Note: `test_rag_api.py`가 없다면 신규 작성하거나 기존 `tests/integration/test_ingestion_graph.py` 등을 참조하여 추가.*

### Manual Verification
1. **Admin UI 접속**: `streamlit run admin/dashboard.py`
2. **채팅 진행**: RAG Playground에서 질문 입력 및 답변 생성.
3. **DB 확인 (Pre)**: Postgres에서 `SELECT count(*) FROM checkpoints WHERE thread_id = ...` 확인 ( > 0).
4. **삭제 실행**: 사이드바 "Delete History" 클릭.
5. **DB 확인 (Post)**: 위 쿼리 결과가 0이어야 함.
6. **New Chat**: "New Chat" 클릭 시 Thread ID 변경 확인.
