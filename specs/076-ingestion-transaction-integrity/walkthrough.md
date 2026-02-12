# Walkthrough: Spec-076 Ingestion Transaction Integrity (Saga Pattern)

## 📋 개요 (Overview)
본 작업은 문서 수집 파이프라인의 원자성(Atomicity)을 보장하기 위해 **Choreography 기반 Saga 패턴**을 도입한 건입니다. 수집 과정 중 어떤 단계에서든 실패가 발생하면, 이전에 생성된 데이터를 자동으로 삭제하는 보상 트랜잭션이 수행됩니다.

## 🚀 주요 변경 사항 (Key Changes)
- **Event-Driven Architecture**: `asyncio` 기반의 내부 `EventBus`를 통해 서비스를 디커플링했습니다.
- **Saga Handlers**: `IngestionSagaHandlers`를 통해 각 단계별 이벤트를 처리하고 상태를 전이합니다.
- **자동 롤백**: `IngestionFailed` 이벤트 수신 시 `DocumentRepository.delete()`를 호출하여 Neo4j 및 ChromaDB 데이터를 정리합니다.
- **상태 세분화**: `JobStatus`를 `COLLECTING`, `INDEXING`, `ROLLING_BACK` 등으로 세분화하여 관측성을 높였습니다.

## 🧪 검증 결과 (Validation Results)

### 1. 통합 테스트 (Integration Tests)
`tests/integration/test_ingestion_rollback.py`를 통해 실패 시 보상 트랜잭션이 작동함을 검증했습니다.

```bash
$ uv run pytest tests/integration/test_ingestion_rollback.py
...
tests/integration/test_ingestion_rollback.py::test_saga_rollback_on_failure PASSED
================ 1 passed in 0.31s ================
```

### 2. 단위 테스트 (Unit Tests)
이벤트 버스의 안정성을 검증했습니다.
```bash
$ uv run pytest tests/unit/core/test_events.py
...
processed 3 items
tests/unit/core/test_events.py ... PASSED
================ 3 passed in 0.11s ================
```

## 📸 증거 로그 (Evidence Logs)
```text
INFO:app.application.saga.ingestion_handlers:Saga Step 1 (Collection) started for job test-job-id
WARNING:app.application.saga.ingestion_handlers:Saga Failure detected at stage Indexing for job test-job-id. Rolling back...
INFO:app.application.saga.ingestion_handlers:Rollback: Deleted document doc1
INFO:app.application.saga.ingestion_handlers:Rollback: Deleted document doc2
```

## ✅ Definition of Done 확인
- [x] 통합 테스트 통과 (롤백 확인)
- [x] 이벤트 로그 확인
- [x] 코드 품질 체크 완료 (`ruff`)
- [x] 모든 문서 한국어로 작성 완료
