# feat(spec-076): Ingestion Transaction Integrity (Saga Pattern)

## 📋 Summary

### 배경 및 목적
수집 파이프라인의 원자성을 보장하기 위해 Choreography 기반의 Saga 패턴을 도입했습니다. 기존의 절차적 방식에서는 중간 단계 실패 시 부분적으로 생성된 데이터(Neo4j 노드, Chroma 덩어리 등)를 정리하기 어려웠으나, 이벤트 중심 아키텍처와 보상 트랜잭션(Rollback)을 통해 데이터 무결성을 확보했습니다.

### 주요 변경 사항
- **이벤트 시스템 도입**: `asyncio` 기반 내부 `EventBus` 추가로 각 단계를 비동기적으로 분리
- **도메인 이벤트 정의**: `IngestionStarted`부터 `DataIndexed`까지 단계별 이벤트 및 `IngestionFailed` 정의
- **Saga 핸들러 구현**: 단계별 상태 업데이트 및 성공/실패 시 후속 조치(보상 트랜잭션 포함) 오케스트레이션
- **레포지토리 인프라 보강**: Neo4j 및 ChromaDB에서 문서 및 연관 덩어리를 완전히 삭제하는 `delete` 메서드 구현
- **Job 상태 관리 세분화**: `COLLECTING`, `EXTRACTING`, `CHUNKING`, `INDEXING` 등 상세 상태 추적 지원

## 🎯 Key Review Points
1. **Saga Choreography**: 각 핸들러가 이벤트를 받고 다음 이벤트를 발행하는 흐름이 자연스러운지, 결합도가 충분히 낮아졌는지 확인 부탁드립니다.
2. **보상 트랜잭션 (Rollback)**: `handle_failed`에서 수행하는 문서 삭제 로직이 모든 저장소(Neo4j, Chroma)에서 안전하게 수행되는지 검토가 필요합니다.
3. **Idempotency**: 핸들러 중복 등록 방지 로직(`_registered` 플래그) 및 핸들러의 재진입 가능성을 확인해 주세요.
4. **Error Handling**: Pydantic `ValidationError`나 LLM 반환값 `None` 등 예외 상황이 `IngestionFailed`로 적절히 전환되는지 확인이 필요합니다.

## 🧪 Verification

### Automated Tests
```bash
# Core EventBus Unit Tests
uv run pytest tests/unit/core/test_events.py

# Saga Integration & Rollback Tests
uv run pytest tests/integration/test_ingestion_rollback.py

# E2E Scenario Verification
uv run pytest tests/integration/scenarios/test_ingestion_scenarios.py::TestIngestionScenarios::test_web_ingestion_with_special_characters_url
```
**테스트 결과 요약:**
- ✅ `EventBus` 구독/발행 기능 확인
- ✅ `test_saga_rollback_on_failure`: 실패 시 Neo4j/Chroma 데이터 삭제 확인
- ✅ `test_web_ingestion_with_special_characters_url`: 전체 Saga 흐름 성공 확인

### Manual Verification (Scenarios)
1. **실패 시 롤백**: 수집 과정 중 인위적으로 오류(추출 실패 등)를 발생시키고, Neo4j와 ChromaDB에서 partial 데이터가 남지 않는 것을 확인했습니다.
2. **상태 모니터링**: 수집 진행 중 Job의 상태가 실시간으로 `COLLECTING` -> `EXTRACTING` 등의 상태로 변화하는 것을 로그와 DB를 통해 확인했습니다.

## 📦 Files Changed

### 🆕 New Files
- `app/core/events.py`: 내부 비동기 이벤트 버스 싱글톤
- `app/domain/events/ingestion_events.py`: 수집 관련 도메인 이벤트 정의
- `app/application/saga/ingestion_handlers.py`: Saga 단계별 핸들러 및 롤백 로직
- `tests/unit/core/test_events.py`: EventBus 단위 테스트
- `tests/integration/test_ingestion_rollback.py`: Saga 롤백 통합 테스트

### 🛠 Modified Files
- `app/application/services/ingestion.py`: `ingest_url`을 이벤트 발행 방식으로 리팩토링
- `app/infrastructure/repositories/neo4j_document_repository.py`: Async `delete` 구현
- `app/infrastructure/repositories/chroma.py`: Async `delete` 구현
- `app/infrastructure/repositories/composite.py`: Composite `delete` 구현
- `app/domain/entities/job.py`: `JobStatus` Enum 추가
- `app/interfaces/api/v1/endpoints/ingest.py`: 서비스 호출 방식 변경
- `app/interfaces/api/dependencies.py`: Saga 핸들러 싱글톤 등록 로직 추가

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료 (본 문서)
- [x] Ruff lint 및 format 확인 완료
