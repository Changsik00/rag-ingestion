# Task List: Spec-058 (API Input Validation & Error Handling)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] User Plan Accept

---

## Task 1: DTO Validation & Schema Improvement
- [x] `IngestRequest` 확장 및 `ChunkingConfigDTO` 연동 (`app/interfaces/api/v1/dto/ingest.py`)
- [x] `AdvancedSettings` 및 `ChatRequest` 검증 강화 (`app/interfaces/api/v1/dto/rag.py`)
- [x] Commit: `feat(spec-058): enhance API DTO validation schemas`

## Task 2: Standardized Error Handling
- [x] `RequestValidationError` 전역 핸들러 구현 (`app/interfaces/api/error_handlers.py`)
- [x] `HTTPException` 및 기타 기본 예외 커스터마이징
- [x] 에러 코드(`VALIDATION_ERROR` 등) 정의 및 매핑
- [x] Commit: `feat(spec-058): implement standardized global error handlers`

## Task 2.5: Admin UI Improvement (User Request)
- [x] `APIClient._handle_response` 개선: 표준 에러 JSON 파싱 및 포맷팅 (`admin/utils/api_client.py`)
- [x] Commit: `feat(spec-058): improve admin api client error display`

## Task 3: Verification & Integration Tests
- [x] API 유효성 검증 통합 테스트 작성 (`tests/integration/functional/test_api_validation.py`)
- [x] 전체 기능 테스트 실행 및 사이드 이펙트 확인
- [ ] Commit: `test(spec-058): add comprehensive API validation tests`

## Task 4: PR Creation & Archiving
- [x] Code Quality Check (`ruff`)
- [x] `walkthrough.md` 및 `pr_description.md` 작성
- [x] PR 생성 (`gh pr create`)
