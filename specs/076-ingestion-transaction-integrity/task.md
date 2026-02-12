# Task List: Spec-076

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: 환경 구성 및 기초 인프라 (Setup & Core)
### 1-1. 브랜치 생성
- [x] 브랜치 생성: `git checkout -b feature/076-ingestion-transaction-integrity`
- [x] Commit: `feat(spec-076): create feature branch`

### 1-2. 내부 이벤트 버스 구현
- [x] Test Case 작성: `tests/unit/core/test_events.py`
- [x] EventBus 구현: `app/core/events.py`
- [x] Test 실행 및 검증
- [x] Commit: `feat(spec-076): implement internal async event bus`

---

## Task 2: 도메인 이벤트 및 인터페이스 확장 (Domain & Interface)
### 2-1. 도메인 이벤트 정의
- [x] 이벤트 정의: `app/domain/events/ingestion_events.py`
- [x] Commit: `feat(spec-076): define ingestion domain events`

### 2-2. Repository 인터페이스 수정
- [x] `delete` 메서드 추가: `app/domain/interfaces/document_repository.py`
- [x] Commit: `refactor(spec-076): add delete method to document repository interface`

---

## Task 3: 인프라 연동 및 보상 트랜잭션 (Infrastructure & Compensation)
### 3-1. Composite Repository 구현
- [x] `delete` 구현: `app/infrastructure/repositories/composite.py`
- [x] Commit: `feat(spec-076): implement delete in composite repository`

### 3-2. Neo4j/Chroma 삭제 로직 보강 (필요시)
- [x] 개별 레포지토리 `delete` 확인 및 보완 (Composite에서 핸들링)
- [x] Commit: `feat(spec-076): ensure hard delete for neo4j and chroma`

---

## Task 4: Saga 핸들러 및 리팩토링 (Saga & Refactoring)
### 4-1. 인코딩/인덱싱 핸들러 구현
- [x] 핸들러 구현: `app/application/saga/ingestion_handlers.py`
- [x] Commit: `feat(spec-076): implement saga handlers for ingestion steps`

### 4-2. Ingestion 서비스 리팩토링
- [x] 이벤트 중심 진입점으로 변경: `app/application/services/ingestion.py`
- [x] Commit: `refactor(spec-076): convert ingestion service to event-driven`

---

## Task 5: 통합 검증 및 마무리 (Verification & PR)
### 5-1. 롤백 시나리오 검증
- [x] 통합 테스트 작성: `tests/integration/test_ingestion_rollback.py`
- [x] 통합 테스트 실행 (Pass)
- [x] Commit: `test(spec-076): add ingestion rollback integration test`

### 5-2. 서비스 안정성 체크
- [x] `uv run ruff check . --fix`
- [x] `uv run pytest`
- [x] **Walkthrough 작성**: `specs/076-ingestion-transaction-integrity/walkthrough.md`
- [x] **PR Description 작성**: `specs/076-ingestion-transaction-integrity/pr_description.md`
- [x] **Archive Commit**: `docs(spec-076): archive walkthrough and pr description`
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 5개  
**예상 커밋 수**: 약 10개  
**현재 진행**: DONE
