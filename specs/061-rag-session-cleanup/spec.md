# Spec-061: RAG Session Manual Cleanup & Admin Actions

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
- Admin Dashboard (`4_RAG_Playground.py`)에서 세션을 초기화하거나 삭제하는 기능이 "Advanced Settings" 내부에 숨겨져 있어 접근성이 낮습니다.
- Spec 060에서 도입된 `AsyncPostgresSaver`는 기본적으로 `adelete_thread` 메서드를 제공하지 않을 가능성이 높아, `reset_session` API가 실제로 DB 데이터를 삭제하지 못할 수 있습니다 (`Not Supported` 반환).

### 문제점
- 테스트 진행 시 이전 대화 문맥이 섞이는 것을 방지하기 위해 빈번한 "새 채팅" 생성이 필요하지만 UI가 불편합니다.
- 데이터베이스에 테스트용 세션 데이터(`checkpoints`, `writes`)가 무한히 쌓입니다.

### 해결 방안
- **Backend**: Postgres DB에서 특정 `thread_id`와 관련된 모든 데이터를 삭제하는 로직(`delete_session_data`)을 직접 구현합니다.
- **Frontend**: "New Chat" 및 "Delete History" 버튼을 사이드바로 이동하여 접근성을 높입니다.

## 📊 개념도 (Conceptual Architecture)
```mermaid
graph TD
    User[Admin User] -->|Click 'Delete History'| UI[Streamlit Sidebar]
    UI -->|POST /rag/sessions/{id}/reset| API[FastAPI Backend]
    API -->|Depends| Checkpointer[AsyncPostgresSaver]
    API -->|Execute SQL| DB[(Postgres DB)]
    
    DB -- Delete --> Checkpoints[Checkpoints Table]
    DB -- Delete --> Writes[Checkpoint Writes Table]
```

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **세션 삭제 (Hard Delete)**: `thread_id`를 기준으로 `checkpoints`, `checkpoint_blobs`, `checkpoint_writes` 테이블에서 관련 데이터를 모두 삭제해야 합니다.
2. **UI 접근성 개선**: "New Chat"과 "Delete Thread" 버튼을 RAG Playground 사이드바 상단에 배치해야 합니다.
3. **피드백**: 삭제 성공 시 UI에 명확한 토스트 메시지를 표시하고 대화 내용을 초기화해야 합니다.

### Non-Functional Requirements
1. **안전성**: 삭제 작업은 Transaction 내에서 원자적으로(Atomically) 수행되어야 합니다.

## ✅ Definition of Done
1. Admin UI 사이드바에서 "New Chat" 클릭 시 새로운 Thread ID가 생성되고 채팅창이 초기화된다.
2. Admin UI 사이드바에서 "Delete History" 클릭 시 Postgres DB에서 해당 Thread ID의 데이터가 완전히 삭제된다.
3. `POST /rag/sessions/{id}/reset` 호출 시 200 OK와 함께 실제 삭제가 수행된다.
