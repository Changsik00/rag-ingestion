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

### Automated Tests
```bash
uv run pytest tests/integration/functional/test_postgres_persistence.py -v
```
**테스트 결과 요약:**
- ✅ `test_postgres_persistence_flow`: 통과 (Connection, Table Creation, Graph Persistence, Retrieval 검증 완료)

### Manual Verification (Scenarios)
1. **Docker Health Check**: `docker-compose up -d postgres` 후 5432 포트 정상 Listen 확인.
2. **Setup**: 앱 실행 시 `lifespan`에서 `await saver.setup()`이 호출되어 테이블(`checkpoints` 등)이 자동 생성됨.

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
