# feat(spec-076): Ingestion Transaction Integrity (Saga Pattern)

## 📋 Summary

### 배경 및 목적
수집 파이프라인의 원자성을 보장하기 위해 Choreography 기반의 Saga 패턴을 도입했습니다. 기존의 절차적 방식에서는 중간 단계 실패 시 부분적으로 생성된 데이터(Neo4j 노드, Chroma 덩어리 등)를 정리하기 어려웠으나, 이벤트 중심 아키텍처와 보상 트랜잭션(Rollback)을 통해 데이터 무결성을 확보했습니다.

### 주요 변경 사항
- **Before**: `Ingestion` 서비스가 모든 수집 단계를 동기적으로 직접 제어하며, 실패 시 부분 데이터가 잔류함.
- **After**: `EventBus`를 통한 비동기적 단계 전이 및 실패 이벤트 발생 시 자동 `Rollback` 수행.
- [x] 내부 비동기 `EventBus` 싱글톤 구현
- [x] 단계별 도메인 이벤트 정의 및 발행 로직 적용
- [x] 보상 트랜잭션을 위한 저장소(Neo4j, Chroma) `delete` 메서드 구현
- [x] 수집 단계별 상세 상태 추적 지원 (`COLLECTING`, `INDEXING` 등)

## 🎯 Key Review Points (리뷰어 체크리스트)
리뷰 시 다음 항목들을 중점적으로 확인 부탁드립니다:
1. **Saga Choreography**: 각 핸들러가 이벤트를 받고 다음 이벤트를 발행하는 흐름이 자연스러운지 확인 (결합도 확인).
2. **보상 트랜잭션 (Rollback)**: `handle_failed`에서 수행하는 문서 삭제 로직이 모든 저장소에서 원자적으로 동작하는지 확인.
3. **Singleton Safety**: `IngestionSagaHandlers`와 `EventBus`가 테스트 환경에서 싱글톤 오염 없이 동작하는지 확인.
4. **Metadata Integrity**: `source_id`, `source_url` 등 필수 메타데이터가 모든 단계에서 유실 없이 전달되는지 확인.

## 🧪 Verification (검증 가이드)

### Automated Tests
아래 명령어를 통해 핵심 기능과 롤백 로직을 검증할 수 있습니다:
```bash
# 핵심 Saga 흐름 및 롤백 검증
uv run pytest tests/integration/test_ingestion_rollback.py tests/integration/scenarios/test_ingestion_scenarios.py
```
**테스트 결과 요약:**
- ✅ `test_saga_rollback_on_failure`: 단계별 실패 시 데이터 정합성 유지 확인
- ✅ `test_web_ingestion_with_chunking_verification`: 전체 워크플로우 성공 확인

### Manual Verification (Scenarios)
1. **실패 시 롤백 확인**: 수집 과정 중간에 인위적인 오류를 주입하고, 대시보드에서 `FAILED` 상태를 확인한 뒤 Neo4j/ChromaDB에 파편 데이터가 남지 않았는지 확인합니다.
2. **상태 모니터링**: 수집 진행 중 `GET /v1/jobs/{job_id}` 호출을 통해 상태가 실시간으로 변경되는지 확인합니다.

## 📦 Files Changed

### 🆕 New Files
- `app/core/events.py`: 비동기 이벤트 버스
- `app/domain/events/ingestion_events.py`: 도메인 이벤트 정의
- `app/application/saga/ingestion_handlers.py`: Saga 코디네이션 핸들러
- `tests/unit/core/test_events.py`: 이벤트 버스 테스트
- `tests/integration/test_ingestion_rollback.py`: 롤백 통합 테스트

### 🛠 Modified Files
- `app/application/services/ingestion.py`: 서비스 진입점 리팩토링
- `app/infrastructure/repositories/composite.py`: Rollback용 삭제 로직 통합
- `app/interfaces/api/dependencies.py`: Saga 핸들러 의존성 주입 최적화
- `tests/integration/scenarios/test_ingestion_scenarios.py`: Saga 기반 테스트 대응

**Total:** 14 files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과 (13/13)
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료 (본 문서)
- [x] Ruff lint 및 format 확인 완료
