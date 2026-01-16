# Task Checklist - Spec 004: 비동기 처리 및 상태 추적 (Async Processing)

## 1. 환경 및 문서 설정 (Environment & Docs)
- [x] Feature Branch 생성 (`feature/spec-004`)
- [x] Spec 문서 작성 (Korean)
- [x] Implementation Plan 승인

## 2. API Layer (API 계층 비동기화)
> **TDD Cycle**: Test (Fail) -> Implement -> Verify (Pass) -> Commit
- [ ] **`POST /ingest/web` 리팩토링**
    - [ ] `main.py`: `BackgroundTasks` 주입 및 202 응답 코드로 변경
    - [ ] `test_async_ingest.py` 작성 및 검증 (202 Accepted, Job ID 반환 확인)
- [ ] **`POST /jobs/{job_id}/retry` 리팩토링**
    - [ ] `endpoints/jobs.py`: 재시도 로직 비동기화
    - [ ] 통합 테스트 업데이트 및 검증

## 3. UseCase Layer (비동기 로직 분리)
- [ ] **`IngestionService` 구조 변경**
    - [x] `create_job` (동기: Job 생성) 메서드 분리
    - [x] `process_job` (비동기: 실제 수행) 메서드 분리
    - [ ] 단위 테스트 (`test_usecases.py`) 업데이트 및 통과 확인

## 4. 최종 검증 (Final Verification)
- [ ] 전체 테스트 슈트 실행 (`make test` or `uv run pytest`)
- [ ] 매뉴얼 테스트 (Swagger UI & Dashboard 연동 확인)
