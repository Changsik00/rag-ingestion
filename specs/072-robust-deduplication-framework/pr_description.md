# feat(spec-072): robust deduplication framework completion

## 📋 Summary

### 배경 및 목적

Spec 065에서 구현한 Deduplication Framework의 핵심 기능을 완성하고, Admin 관리 기능을 추가하여 **Production-Ready Deduplication System**을 구축합니다.

**해결하는 문제:**
- ✅ 중복으로 Skip된 Job을 추적하고 사유를 확인할 방법 부재
- ✅ Admin이 강제로 재수집할 수 있는 기능 부재
- ✅ Content Hash가 계산되지 않아 `ContentsStrategy` 미사용
- ✅ Admin UI에서 SKIPPED 상태 Job 조회 불가

### 주요 변경 사항

**Before (Spec 065):**
- ✅ 4가지 Deduplication Strategy (ID, Metadata, TTL, Contents)
- ✅ DeduplicationFactory 패턴
- ❌ Skip된 Job 추적 불가
- ❌ Admin 재수집 기능 없음

**After (Spec 072):**
- [x] `JobStatus.SKIPPED` + `skip_reason` 필드 추가
- [x] `force_refresh` 파라미터로 중복 체크 우회
- [x] Content Hash 계산 (SHA-256)
- [x] Admin API: `GET /admin/jobs`, `POST /admin/jobs/{id}/force-refresh`
- [x] Admin UI: Status 필터, Skip Reason 컬럼, Force Refresh 버튼

## 🎯 Key Review Points

1. **Entity Layer (`app/domain/entities/job.py`)**:
   - `skip_reason: str | None` 필드 추가 - 중복 Skip 사유 저장

2. **Service Layer (`app/application/services/ingestion.py`)**:
   - `process_job(job_id, force_refresh=False)` - Admin Force Refresh 지원
   - Content Hash 계산 로직 (`hashlib.sha256`) 추가
   - Deduplication 감지 시 `skip_reason` 자동 저장

3. **Repository Layer (`app/infrastructure/repositories/neo4j_job_repository.py`)**:
   - `get_jobs(status, limit)` 메서드 구현 - Status 필터링
   - Neo4j schema 업데이트 (`skip_reason` 필드 추가)

4. **Admin API (`app/interfaces/api/admin_jobs.py`)** - NEW:
   - `GET /admin/jobs?status={status}&limit={limit}` - 필터링된 Job 목록
   - `POST /admin/jobs/{job_id}/force-refresh` - 강제 재수집

5. **Admin UI (`admin/pages/0_Job_Queue.py`)**:
   - Status 필터 Dropdown (ALL/PENDING/RUNNING/COMPLETED/FAILED/SKIPPED)
   - Skip Reason 컬럼 추가
   - Force Refresh UI (Job ID 입력 → 버튼 클릭)

## 🧪 Verification

### Automated Tests

**E2E Tests (`tests/e2e/test_deduplication_end_to_end.py`)** - NEW:
```bash
docker-compose up -d neo4j chromadb
uv run pytest tests/e2e/test_deduplication_end_to_end.py -v --e2e
```

**테스트 결과 요약:**
- ✅ `test_duplicate_job_is_skipped`: 동일 URL 2번 수집 시 2번째 SKIPPED 확인
- ✅ `test_force_refresh_bypasses_deduplication`: force_refresh로 중복 체크 우회 확인
- ✅ `test_skip_reason_persisted_in_database`: skip_reason DB 저장 확인

**Integration Tests (기존):**
```bash
uv run pytest tests/integration/test_ingestion_deduplication.py -v
```

### Manual Verification (Scenarios)

#### 시나리오 1: Admin UI - Skipped Jobs 조회
```bash
uv run streamlit run admin/dashboard.py
```
1. "📋 Job Queue" 페이지 접속
2. Status 필터에서 "SKIPPED" 선택
3. Skip Reason 컬럼에 중복 사유 표시 확인
4. **결과**: SKIPPED 상태 Job 목록 및 사유 확인 가능

#### 시나리오 2: Admin UI - Force Refresh
1. SKIPPED 상태 Job ID 복사 (예: `abc-123`)
2. "Force Refresh" 섹션에 Job ID 입력
3. "Force Refresh" 버튼 클릭
4. **결과**: 성공 메시지 표시, Job 상태가 RUNNING/COMPLETED로 변경

#### 시나리오 3: API - Deduplication Flow
```bash
# Backend 실행
uv run uvicorn app.interfaces.api.main:app --reload

# 동일 URL 2번 수집
curl -X POST "http://localhost:8000/v1/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/test"}'

curl -X POST "http://localhost:8000/v1/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/test"}'
```
- **결과**: 두 개의 Job 생성 (서로 다른 job_id)
- **첫 번째 Job**: COMPLETED 상태
- **두 번째 Job**: SKIPPED 상태, skip_reason에 첫 번째 Job ID 포함
- **Neo4j 확인**: `MATCH (j:IngestionJob {status: "SKIPPED"}) RETURN j.skip_reason`
- **Job Queue UI**: SKIPPED 상태 Job 확인 가능

#### 시나리오 4: API - Force Refresh
```bash
curl -X POST "http://localhost:8000/admin/jobs/{job_id}/force-refresh"
```
- **결과**: SKIPPED 상태 Job이 재처리되어 COMPLETED 상태로 변경
- **결과**: `content_hash` 필드가 계산되어 저장됨

## 📦 Files Changed

### 🆕 New Files
- `app/interfaces/api/admin_jobs.py` (+62): Admin API endpoints (GET, POST)
- `tests/e2e/test_deduplication_end_to_end.py` (+145): E2E 테스트 3개
- `docs/architecture/deduplication.md` (+170): Architecture 문서
- `specs/072-robust-deduplication-framework/walkthrough.md` (+281): 구현 Walkthrough
- `specs/072-robust-deduplication-framework/pr_description.md` (+152): PR Description

### 🛠 Modified Files
- `app/domain/entities/job.py` (+1, -0): `skip_reason` 필드 추가
- `app/application/services/ingestion.py` (+31, -10): `force_refresh`, Content Hash 로직
- `app/domain/interfaces/job_repository.py` (+7, -0): `get_jobs()` 메서드 선언
- `app/infrastructure/repositories/neo4j_job_repository.py` (+30, -2): `get_jobs()` 구현, `skip_reason` 저장
- `app/interfaces/api/main.py` (+4, -0): Admin API Router 등록
- `admin/pages/0_Job_Queue.py` (+43, -8): Status 필터, Force Refresh UI

**Total:** 11 files changed (+605, -20)

## ✅ Definition of Done

- [x] 모든 E2E 테스트 작성 완료 (3개 테스트)
- [x] Integration 테스트 기존 유지
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
- [x] Documentation 작성 (`docs/architecture/deduplication.md`)
- [x] Admin UI 기능 구현 완료
- [ ] Manual Verification (Reviewer/Deployer 진행 필요)
  - [ ] Admin UI 동작 확인
  - [ ] Deduplication Flow 확인
  - [ ] Force Refresh API 테스트

## 🔗 Related Specs

- Built on: [Spec 065: Deduplication Strategies](../065-deduplication-strategies/spec.md)
- Follows: [Spec 071: ChromaDB Upsert Logic](../071-chromadb-upsert-logic/spec.md)
- References: [Spec 068: RAG Architecture Review](../068-rag-architecture-review/spec.md)

## 📝 Deployment Notes

**Breaking Changes:** 없음

**New Environment Variables:** 없음

**Database Migrations:** 
- Neo4j: `skip_reason` 필드가 자동으로 추가됨 (Optional field)

**Backwards Compatibility:**
- ✅ `force_refresh` 파라미터는 Optional (기본값 `False`)
- ✅ 기존 Deduplication 로직 100% 유지
- ✅ Admin API는 `/admin` prefix로 분리됨
