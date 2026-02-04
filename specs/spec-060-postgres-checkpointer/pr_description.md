# feat(spec-060): migrate checkpointer to postgres & adopt messages state

## 📋 Summary

### 배경 및 목적
기존 SQLite 기반의 Checkpointer는 단일 파일 락(db locked) 이슈로 인해 동시성 처리가 어렵고, 확장이 불가능했습니다. 이를 해결하기 위해 PostgreSQL(`AsyncPostgresSaver`)로 Checkpointer를 마이그레이션하고, LangGraph 표준인 `MessagesState`를 도입하여 상태 관리를 개선했습니다.

### 주요 변경 사항
- [x] **Postgres Checkpointer 도입**: `AsyncSqliteSaver` 제거 및 `AsyncPostgresSaver` + `AsyncConnectionPool` 적용
- [x] **Infrastructure 추가**: `docker-compose.yml`에 Postgres v16 서비스 추가 및 Config 연동
- [x] **MessagesState 마이그레이션**: 커스텀 `steps_history`를 제거하고 LangGraph 표준 `MessagesState` 사용
- [x] **Lifespan 관리**: DB Connection Pool을 FastAPI Lifespan에서 효율적으로 관리하도록 개선

## 🎯 Key Review Points
1.  **Dependencies (`app/interfaces/api/dependencies.py`)**: `get_checkpointer` 함수가 Global Pool에서 Connection을 받아 `AsyncPostgresSaver`를 Yield 하는 방식이 적절한지 확인 필요.
2.  **State Management (`app/infrastructure/ai/ingestion_nodes.py`)**: 각 Node가 `steps_history` 대신 `AIMessage`를 리턴하여 `messages`에 누적되는 흐름이 올바른지.
3.  **Migration Strategy**: 기존 SQLite 데이터는 마이그레이션하지 않고, 새로운 Postgres 테이블에서 시작하는 전략입니다.

## 🧪 Verification

### 1. Automated Tests (CLI)
새로 추가된 통합 테스트를 수행하여 Postgres 연결 및 데이터 저장을 검증할 수 있습니다.
```bash
# 통합 테스트 실행
uv run pytest tests/integration/functional/test_postgres_persistence.py -v
```
**예상 결과:**
- ✅ `test_postgres_persistence_flow`: PASSED
- DB Table (`checkpoints`, `checkpoint_writes`)에 데이터가 정상적으로 INSERT 조회됨을 확인.

### 2. Manual Verification (Admin Dashboard)
실제 백엔드 서버를 띄우고 Admin 페이지에서 검증하는 방법입니다.

1.  **Server Start**:
    ```bash
    # Postgres 컨테이너 실행
    docker-compose up -d postgres
    
    # 서버 실행
    uv run uvicorn app.interfaces.api.main:app --reload
    ```
2.  **Admin Dashboard 접속**:
    - 브라우저에서 Admin URL 접속 (예: `http://localhost:8000/docs` 또는 프론트엔드 대시보드)
    - **"Trigger Ingestion Job"** (POST `/api/v1/ingest`) API 호출 또는 버튼 클릭.
3.  **결과 확인**:
    - Job이 **Successful** 상태로 완료되는지 확인.
    - 서버 로그에 `LangGraph Adapter: Checkpoints have been reset` 또는 Postgres 관련 에러가 없는지 확인.
    - (옵션) DB 직접 접속하여 데이터 확인:
        ```bash
        docker exec -it rag-postgres psql -U user -d ragdb -c "SELECT count(*) FROM checkpoints;"
        ```

## 📦 Files Changed

### 🆕 New Files
- `tests/integration/functional/test_postgres_persistence.py`: Postgres 통합 테스트
- `app/core/database.py`: Global DB Pool 선언

### 🛠 Modified Files
- `pyproject.toml`: 의존성 변경 (sqlite -> postgres)
- `docker-compose.yml`: Postgres 서비스 추가
- `app/interfaces/api/main.py`: AsyncConnectionPool Lifespan 추가
- `app/interfaces/api/dependencies.py`: Checkpointer 주입 로직 변경
- `app/infrastructure/ai/ingestion_orchestrator.py`: Checkpointer Reset 로직(Truncate) 및 초기 상태 변경
- `app/infrastructure/ai/ingestion_nodes.py`: `MessagesState` 대응 (Message 로깅)
- `app/domain/value_objects/ingestion_state.py`: `MessagesState` 상속

**Total:** 12 files changed (including docs)

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
