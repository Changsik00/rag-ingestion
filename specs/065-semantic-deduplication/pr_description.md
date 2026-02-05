# feat(spec-065): Semantic De-Duplication

## 📋 Summary

### 배경 및 목적
기존의 무조건적인 데이터 수집은 불필요한 리소스(저장 공간, 임베딩 비용)를 낭비하고, 검색 결과의 품질을 저하시키는(중복 문서 노출) 문제를 야기했습니다.
이를 해결하기 위해 **Logic-Based Deduplication Strategy**를 도입하여, 데이터 소스의 특성에 따라 메타데이터 비교 또는 콘텐츠 해시 비교를 통해 중복 수집을 방지합니다.

### 주요 변경 사항
- [x] **Deduplication Strategy Pattern 구현**: Metadata 비교 및 Content Hash 비교 전략 도입
- [x] **IngestionJob Schema 개선**: 중복 검사를 위한 `content_hash`, `custom_metadata` 필드 추가
- [x] **Ingestion Pipeline 통합**: 수집 전 중복 체크 및 Skip 로직 구현
- [x] **Admin UI 개선**: "Force Refresh" 옵션 추가

## 🎯 Key Review Points
1.  **DeduplicationFactory & Strategies**: `app/application/services/deduplication_strategies.py`의 전략 선택 및 판별 로직의 적절성.
2.  **Ingestion Integration**: `app/application/services/ingestion.py`에서 중복 체크 시점과 `SKIPPED` 처리의 흐름.
3.  **Entity Expansion**: `IngestionJob` 엔티티 확장의 정합성 (`app/domain/entities/job.py`).

## 🧪 Verification

### Automated Tests
```bash
uv run pytest tests/unit/test_deduplication_strategies.py
uv run pytest tests/integration/test_ingestion_deduplication.py
```
**테스트 결과 요약:**
- ✅ `test_deduplication_strategies.py`: 5개 테스트 통과 (Metadata Match, Hash Match 등)
- ✅ `test_ingestion_deduplication.py`: 2개 테스트 통과 (Duplicate Skip, New Job Process)

### Manual Verification (Scenarios)
1. **Admin UI**: Ingestion 관리 페이지에서 "Force Refresh" 체크박스 상태에 따라 요청 Payload에 `force_refresh`가 올바르게 전달되는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/application/services/deduplication_strategies.py`: 중복 제거 전략 및 Factory 구현
- `tests/unit/test_deduplication_strategies.py`: 전략 단위 테스트
- `tests/integration/test_ingestion_deduplication.py`: Ingestion 통합 테스트

### 🛠 Modified Files
- `app/domain/entities/job.py`: `content_hash`, `custom_metadata`, `SKIPPED` status 추가
- `app/application/services/ingestion.py`: Deduplication Logic 통합
- `app/infrastructure/repositories/neo4j_job_repository.py`: 새로운 필드 Persistence 로직 추가
- `app/interfaces/api/v1/endpoints/ingest.py`: Force Refresh 파라미터 처리
- `admin/pages/0_Ingestion_Management.py`: Force Refresh UI 추가

**Total:** 8 files changed (Test 포함)

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
