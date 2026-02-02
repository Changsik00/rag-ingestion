# Task List: Spec-053 API Standardization

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [ ] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: DTO Foundation (P1)
### 1-1. Common DTOs
- [x] `app/interfaces/api/dto/common.py` 생성 (`BaseResponse`, `ErrorResponse`, `PaginationResponse`)
- [x] Test: `tests/unit/interfaces/api/dto/test_common.py` (Schema Validation)

### 1-2. Domain Specific DTOs
- [x] `app/interfaces/api/dto/jobs.py` 생성 (`JobResponse` 등)
- [x] `app/interfaces/api/dto/rag.py` 생성 (`RAGResponse` 등)
- [x] `app/interfaces/api/dto/system.py` 생성 (`SystemStatusResponse`)

---

## Task 2: Global Exception Handling (P1)
### 2-1. Custom Exceptions
- [x] `app/application/exceptions.py` 생성 (e.g., `EntityNotFoundException`, `DomainValueError`)

### 2-2. Exception Handlers
- [x] `app/interfaces/api/error_handlers.py` 구현
- [x] `app/interfaces/api/main.py`에 핸들러 등록
- [x] Test: `tests/integration/test_error_handling.py` (강제 에러 발생 후 JSON 포맷 검증)

---

## Task 3: Ingestion/Jobs Endpoint Refactoring (P2)
### 3-1. Jobs API Refactoring
- [x] `app/interfaces/api/v1/endpoints/jobs.py`: `list_jobs` -> `list[JobResponse]`
- [x] `app/interfaces/api/v1/endpoints/jobs.py`: `get_job` -> `JobResponse`
- [x] `app/interfaces/api/v1/endpoints/jobs.py`: `get_job_status` -> `JobStatusResponse`
- [x] Test: `tests/integration/tdd/test_api_ingest.py` 수정 및 검증 (via test_api_jobs.py)

### 3-2. Ingest API Refactoring
- [x] `app/interfaces/api/v1/endpoints/ingest.py`: 기존 DTO 활용하여 Response Model 명시 강화

---

## Task 4: RAG Endpoint Refactoring (P2)
### 4-1. RAG API Refactoring
- [x] `app/interfaces/api/dto/rag.py` 생성 (`RAGResponse`, `RetrievalResponse` 등)
- [x] `app/interfaces/api/v1/endpoints/rag.py`: DTO Applying & `try-except` removal
- [x] Test: `tests/integration/bdd/test_reasoning_flow.py` (or created `test_api_rag.py`)(존재하면) 혹은 신규 API 테스트

### 4-2. Entity/Graph API Refactoring
- [x] `app/interfaces/api/v1/endpoints/entities.py` -> `DocumentResponse`
- [x] `app/interfaces/api/v1/endpoints/graph.py`: Remove redundant `try-except` blocks (User Feedback)
- [x] `app/interfaces/api/v1/endpoints/graph.py` -> `GraphResponse` (DTO application)

---

## Task N: Final Cleanup & PR
- [x] Swagger UI (`/docs`) 육안 검증 (Verified via Tests)
- [x] Lint/Format Check
- [/] Walkthrough 작성
- [ ] PR 생성
