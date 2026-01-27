# [Spec-042] DB Reset & Admin UI Persistence Implementation Plan

## Goal Description
Admin UI에서 버튼 클릭 한 번으로 모든 데이터베이스(Neo4j, Chroma, SQLite)를 초기화할 수 있는 기능을 제공하여 테스트 환경을 빠르게 재설정할 수 있게 한다. 또한, RAG Playground에서 새로고침 시에도 대화 이력이 사라지지 않도록 개선하여 UX를 향상시킨다.

## User Review Required
> [!WARNING]
> **DB Reset 기능의 파급력**: 이 기능은 연결된 DB의 **모든 데이터**를 영구적으로 삭제합니다. 실수로 클릭하지 않도록 UI에서 "Confirm" 과정을 반드시 거치도록 구현할 예정입니다.

## Proposed Changes

### Application Layer (Backend)
#### [MODIFY] [admin_api.py](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/admin_api.py)
- `POST /admin/reset` 엔드포인트 추가 (IntegrityRouter 확장).
- `IntegrityService.reset_all()` 호출 연결.

#### [NEW] [integrity_service.py](file:///Users/ck/Project/doit/rag-ingestion/app/application/admin/integrity_service.py)
- `IntegrityService` 클래스 생성.
- `Neo4jStorage`, `ChromaStorage`, `Checkpointer` (SQLite) 각각에 대한 초기화 메서드 호출 및 통합 관리.

### Infrastructure Layer
#### [MODIFY] [neo4j_document_repository.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_document_repository.py)
- `reset_database()` 메서드 추가: `MATCH (n) DETACH DELETE n` 실행.

#### [MODIFY] [chroma.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/chroma.py)
- `reset_collection()` 메서드 추가.

#### [MODIFY] [adapter.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/brain/adapter.py)
- LangGraph Checkpointer 초기화 로직 추가 지점 확인 (또는 SQLite 파일 직접 삭제/Truncate 전략).
- `checkpoints.sqlite` 리셋 기능 구현.

### Presentation Layer (Streamlit)
#### [MODIFY] [4_RAG_Playground.py](file:///Users/ck/Project/doit/rag-ingestion/admin/pages/4_RAG_Playground.py)
- **Sidebar**: "Danger Zone" Expander 추가.
- "Reset System" 버튼 및 `st.popover` 또는 `checkbox`를 이용한 2단계 확인 U.
- `st.session_state.messages` 초기화 및 지속성 로직 보완.

## Verification Plan

### Automated Tests
- `tests/integration/test_integrity_api.py` (New):
  1. 데이터를 일부 넣는다 (Ingest).
  2. Reset API를 호출한다.
  3. DB가 비어있는지 확인한다 (Neo4j Count 0, Chroma Count 0).

### Manual Verification
- **Streamlit UI Test**:
  1. Admin 접속 -> Danger Zone -> Reset 클릭.
  2. Success 메시지 확인.
  3. Graph Explorer 등에서 데이터가 사라졌는지 시각적 확인.
  4. Playground에서 대화 후 새로고침(F5) -> 대화 내용 유지 여부 확인.
