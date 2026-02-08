# Task List: Spec-072 Robust Deduplication Framework

## Progress
- [x] Spec 번호 확정 및 폴더 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept ⏸️

---

## Task 1: JobStatus.SKIPPED Enum 추가

### 1-1. Entity 수정
- [ ] `app/domain/entities/job.py` 수정:
  - `JobStatus` Enum에 `SKIPPED` 추가
  - `IngestionJob`에 `content_hash: str | None` 필드 추가
  - `IngestionJob`에 `skip_reason: str | None` 필드 추가
- [ ] Commit: `feat(spec-072): add SKIPPED status and content_hash to IngestionJob`

### 1-2. Repository Schema 업데이트
- [ ] Neo4j Job Repository 스키마 확인:
  - `IngestionJob` Node가 `content_hash`, `skip_reason` 속성 지원하는지 확인
  - 필요 시 Migration 스크립트 작성
- [ ] Commit: `feat(spec-072): update neo4j job schema for content_hash`

---

## Task 2: Ingestion Service 개선

### 2-1. Force Refresh 파라미터 추가
- [ ] `app/application/services/ingestion.py` 수정:
  - `process_job(job_id: str, force_refresh: bool = False)` 시그니처 변경
  - `force_refresh=True`일 경우 Deduplication Check 우회
- [ ] Commit: `feat(spec-072): add force_refresh parameter to ingestion service`

### 2-2. Content Hash 계산 로직 추가
- [ ] `app/application/services/ingestion.py`의 `process_job()` 수정:
  - Scrape 결과에서 `hashlib.sha256(result.markdown.encode()).hexdigest()` 계산
  - `job.content_hash` 저장
- [ ] Commit: `feat(spec-072): calculate and store content hash after scraping`

### 2-3. Skip Reason 저장
- [ ] Deduplication 감지 시:
  - `job.status = JobStatus.SKIPPED` 설정
  - `job.skip_reason = f"Duplicate detected by {strategy.__class__.__name__}"` 저장
  - Repository에 업데이트
- [ ] Commit: `feat(spec-072): store skip reason when deduplication detected`

---

## Task 3: Admin API 추가

### 3-1. Job 목록 조회 API
- [ ] `app/interfaces/api/admin/jobs.py` 생성:
  - `GET /admin/jobs?status={status}&source_type={type}` Endpoint
  - JobRepository에 `get_jobs(status, source_type, limit)` 메서드 추가 필요
- [ ] Commit: `feat(spec-072): add admin jobs list api endpoint`

### 3-2. Force Refresh API
- [ ] `app/interfaces/api/admin/jobs.py`에 추가:
  - `POST /admin/jobs/{job_id}/force-refresh` Endpoint
  - Ingestion Service 호출 시 `force_refresh=True` 전달
- [ ] Commit: `feat(spec-072): add force refresh api endpoint`

### 3-3. Repository 메서드 구현
- [ ] `app/infrastructure/repositories/neo4j_job_repository.py` 수정:
  - `get_jobs(status, source_type, limit)` 메서드 구현
  - Cypher Query: `MATCH (j:IngestionJob) WHERE j.status = $status ...`
- [ ] Commit: `feat(spec-072): implement get_jobs method in neo4j repository`

---

## Task 4: Admin UI 추가 (Streamlit)

### 4-1. Skipped Jobs 페이지 생성
- [ ] `admin_ui/pages/jobs.py` 생성 (또는 기존 파일 수정):
  - Status 필터 (Selectbox)
  - Jobs 테이블 표시 (`st.dataframe`)
  - Force Refresh 버튼 및 확인 Modal
- [ ] Commit: `feat(spec-072): add skipped jobs page to admin ui`

### 4-2. Force Refresh 동작 구현
- [ ] Admin UI에서 Force Refresh 버튼 클릭 시:
  - `POST /admin/jobs/{job_id}/force-refresh` API 호출
  - 성공 시 `st.success()` 메시지
- [ ] Commit: `feat(spec-072): implement force refresh button in admin ui`

---

## Task 5: E2E 테스트 작성

### 5-1. E2E 테스트 파일 생성
- [ ] `tests/e2e/test_deduplication_end_to_end.py` 생성:
  - `test_duplicate_job_is_skipped()`: 동일 URL 2번 수집 시 2번째 SKIPPED 확인
  - `test_force_refresh_bypasses_deduplication()`: Force Refresh 동작 확인
- [ ] Docker Compose로 Neo4j/ChromaDB 실행 후 테스트
- [ ] Commit: `test(spec-072): add e2e tests for deduplication`

### 5-2. E2E 테스트 실행
- [ ] 명령어: `docker-compose up -d neo4j chromadb && uv run pytest tests/e2e/test_deduplication_end_to_end.py -v --e2e`
- [ ] 예상 결과: 2개 테스트 모두 PASS ✅
- [ ] Commit: `docs(spec-072): add e2e test execution guide`

---

## Task 6: Integration 테스트 확장

### 6-1. Force Refresh 테스트 추가
- [ ] `tests/integration/test_ingestion_deduplication.py`에 추가:
  - `test_force_refresh_bypasses_deduplication()`: Mock 기반 테스트
- [ ] 실행: `uv run pytest tests/integration/test_ingestion_deduplication.py -v`
- [ ] Commit: `test(spec-072): add force refresh integration test`

---

## Task 7: Manual Verification

### 7-1. Admin UI 동작 확인
- [ ] Streamlit Admin UI 실행: `uv run streamlit run admin_ui/app.py`
- [ ] Skipped Jobs 페이지 접속하여 필터링 동작 확인
- [ ] Force Refresh 버튼 클릭 시 재수집 확인
- [ ] 스크린샷 캡처 → `specs/072/walkthrough.md`에 첨부

### 7-2. 실제 중복 수집 시나리오
- [ ] FastAPI 서버 실행: `uv run uvicorn app.main:app --reload`
- [ ] 동일 URL을 2번 POST하여 2번째가 SKIPPED되는지 확인
- [ ] Neo4j Browser에서 `skip_reason` 확인
- [ ] 결과 기록 → `walkthrough.md`

---

## Task 8: Documentation 업데이트

### 8-1. Architecture 문서 작성
- [ ] `docs/architecture/deduplication.md` 생성:
  - 4가지 Strategy 설명
  - Factory 선택 로직
  - Force Refresh 사용법
- [ ] Commit: `docs(spec-072): add deduplication architecture document`

### 8-2. Walkthrough 작성
- [ ] `specs/072/walkthrough.md` 작성:
  - 변경 사항 요약
  - E2E 테스트 결과
  - Admin UI 스크린샷
- [ ] Commit: `docs(spec-072): add walkthrough with test results`

---

## Task 9: PR Creation & Archiving (Mandatory)

- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/072/walkthrough.md`
- [ ] **PR Description 작성**: `specs/072/pr_description.md` (템플릿 준수)
- [ ] **Archive Commit**: 위 파일을 `specs/`에 커밋 (`docs(spec-072): archive walkthrough and pr description`)
- [ ] Create PR:
  ```bash
  gh pr create \
    --title "feat(spec-072): robust deduplication framework completion" \
    --body-file specs/072-robust-deduplication-framework/pr_description.md
  ```

---

## Summary
**총 Task**: 9개  
**예상 커밋 수**: ~15개  
**현재 진행**: Planning → **User Plan Accept 대기 중** ⏸️
