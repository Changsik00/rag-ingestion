# Plan: Spec 009 - Testing Strategy Improvement

## 📋 개요 (Overview)

이 Plan은 테스트 전략을 개선하여 통합 환경에서만 발견되는 버그를 단위 테스트 단계에서 조기 발견할 수 있도록 테스트 인프라를 강화합니다.

**핵심 목표:**
1. Contract Testing 도입으로 인터페이스-구현체 계약 보장
2. Integration Test 시나리오 강화로 런타임 버그 조기 발견
3. 테스트 전략 문서화로 향후 Spec의 품질 보증

---

## 🌿 브랜치 전략 (Branch Strategy)

```bash
# Task 1에서 실행
git checkout -b feature/009-testing-strategy
```

---

## 📂 변경 파일 요약 (File Changes Summary)

### 새로 생성할 파일 (NEW)

#### Documentation
- `docs/testing_strategy.md` - 테스트 전략 가이드 문서

#### Contract Tests
- `tests/contracts/__init__.py` - Contract tests 패키지 초기화
- `tests/contracts/test_storage_contract.py` - DocumentRepository 계약 테스트
- `tests/contracts/test_job_repository_contract.py` - JobRepository 계약 테스트
- `tests/contracts/test_llm_contract.py` - LLM 인터페이스 계약 테스트
- `tests/contracts/test_scraper_contract.py` - Scraper 계약 테스트

#### Integration Test Scenarios
- `tests/integration/scenarios/__init__.py` - 시나리오 테스트 패키지
- `tests/integration/scenarios/test_success_flows.py` - 성공 시나리오 테스트 (정상 플로우, extraction on/off, 중복 처리, 다양한 콘텐츠)
- `tests/integration/scenarios/test_failure_flows.py` - 실패 시나리오 테스트 (잘못된 URL, 404, 타임아웃, LLM 실패, 네트워크 오류 등)
- `tests/integration/scenarios/test_edge_cases.py` - Edge Case 테스트 (긴 URL, 특수문자, 큰 페이지, redirect, concurrency)
- `tests/integration/test_dependency_injection.py` - DI Container 검증

### 수정할 파일 (MODIFY)

- `pyproject.toml` - testcontainers 의존성 추가 (선택적)
- `backlog/queue.md` - Spec 010 추가 (이미 완료)

---

## 📝 상세 실행 계획 (Detailed Tasks)

### Task 1: 브랜치 생성 및 테스트 전략 문서 작성

**작업 내용:**
- [x] Feature 브랜치 생성: `feature/testing-strategy-improvement`
- [x] `docs/testing_strategy.md` 작성:
  - 테스트 피라미드 설명 (Unit / Integration / E2E)
  - Contract Testing 가이드
  - Integration Test 원칙
  - Spec별 테스트 체크리스트
  - CI 테스트 전략

**테스트:**
- 문서가 마크다운 형식으로 올바르게 작성되었는지 확인

**커밋 메시지:**
```
docs: add comprehensive testing strategy guide
```

---

### Task 2: Contract Tests 인프라 구축 - Storage

**작업 내용:**
- [x] `tests/contracts/` 디렉토리 생성
- [x] `tests/contracts/__init__.py` 생성
- [x] `tests/contracts/test_storage_contract.py` 작성:
  - `DocumentRepository` 인터페이스를 구현한 모든 클래스 검증
  - `Neo4jStorage`, `ChromaStorage` 등 parametrize로 테스트
  - 생성자 시그니처 검증
  - 인터페이스 메서드 존재 여부 검증

**테스트:**
```bash
pytest tests/contracts/test_storage_contract.py -v
```

**커밋 메시지:**
```
test: add contract tests for DocumentRepository implementations
```

---

### Task 3: Contract Tests - Job Repository

**작업 내용:**
- [x] `tests/contracts/test_job_repository_contract.py` 작성:
  - `JobRepository` 인터페이스 구현체 검증
  - `Neo4jJobRepository` 계약 준수 확인

**테스트:**
```bash
pytest tests/contracts/test_job_repository_contract.py -v
```

**커밋 메시지:**
```
test: add contract tests for JobRepository implementations
```

---

### Task 4: Contract Tests - LLM Interface

**작업 내용:**
- [x] `tests/contracts/test_llm_contract.py` 작성:
  - `LLM` Protocol 구현체 검증
  - `LangChainAdapter` 계약 준수 확인
  - `extract_metadata` 메서드 시그니처 검증

**테스트:**
```bash
pytest tests/contracts/test_llm_contract.py -v
```

**커밋 메시지:**
```
test: add contract tests for LLM interface implementations
```

---

### Task 5: Contract Tests - Scraper Interface

**작업 내용:**
- [x] `tests/contracts/test_scraper_contract.py` 작성:
  - `Scraper` Protocol 구현체 검증
  - `BasicScraper` 계약 준수 확인
  - `scrape` 메서드 시그니처 검증

**테스트:**
```bash
pytest tests/contracts/test_scraper_contract.py -v
```

**커밋 메시지:**
```
test: add contract tests for Scraper interface implementations
```

---

### Task 6: Integration Test - 성공 시나리오 (Success Cases)

**작업 내용:**
- [x] `tests/integration/scenarios/` 디렉토리 생성
- [x] `tests/integration/scenarios/__init__.py` 생성
- [x] `tests/integration/scenarios/test_success_flows.py` 작성:
  
  **시나리오 1: 정상적인 웹 페이지 수집 (기본 플로우)**
  - `POST /ingest/web` 호출 (정상 URL, extraction 활성화)
  - Job ID로 상태 폴링 (PENDING → RUNNING → COMPLETED)
  - `GET /jobs/{job_id}` 응답 검증 (status, result 확인)
  - `GET /documents` 결과 확인 (document 저장 확인)
  - Neo4j에 AtomicDocument 노드 저장 확인
  - ChromaDB에 embedding 저장 확인
  
  **시나리오 2: Extraction 비활성화 플로우**
  - `POST /ingest/web` 호출 (enable_extraction=False)
  - Job이 COMPLETED로 완료되지만 metadata가 비어있음 확인
  
  **시나리오 3: 중복 URL 처리 (멱등성)**
  - 동일한 URL을 두 번 수집
  - 두 번째 수집도 정상 완료 (중복 허용 또는 적절한 처리 확인)
  
  **시나리오 4: 다양한 콘텐츠 타입**
  - HTML 페이지
  - 마크다운 콘텐츠가 있는 페이지
  - 긴 텍스트가 있는 페이지

**테스트:**
```bash
docker-compose up -d
pytest tests/integration/scenarios/test_success_flows.py -v
```

**커밋 메시지:**
```
test: add integration tests for success scenarios
```

---

### Task 7: Integration Test - 실패 시나리오 (Failure Cases)

**작업 내용:**
- [x] `tests/integration/scenarios/test_failure_flows.py` 작성:
  
  **시나리오 1: 잘못된 URL 형식**
  - `POST /ingest/web` 호출 (URL: "not-a-valid-url")
  - 400 Bad Request 응답 확인
  - 에러 메시지가 명확한지 검증
  
  **시나리오 2: 존재하지 않는 URL (404)**
  - `POST /ingest/web` 호출 (URL: "https://example.com/non-existent-page")
  - Job이 FAILED 상태로 전이되는지 확인
  - error 필드에 적절한 에러 메시지 포함 확인
  
  **시나리오 3: 타임아웃 시뮬레이션**
  - 매우 느린 응답을 주는 URL (mock server 사용 또는 실제 slow endpoint)
  - Job이 FAILED로 전이되고 timeout 관련 에러 메시지 확인
  
  **시나리오 4: 접근 불가능한 URL (네트워크 오류)**
  - 존재하지 않는 도메인 (e.g., "https://this-domain-does-not-exist-12345.com")
  - Job FAILED 상태 및 connection error 확인
  
  **시나리오 5: LLM 호출 실패 (API Key 없음 - Mock)**
  - LLM Adapter를 Mock으로 대체하여 에러 발생시키기
  - extraction이 실패해도 Job이 적절히 처리되는지 확인
  - 부분 성공 로직 검증 (document는 저장되지만 metadata는 비어있음)
  
  **시나리오 6: 잘못된 Job ID 조회**
  - `GET /jobs/non-existent-job-id`
  - 404 Not Found 응답 확인
  
  **시나리오 7: 빈 콘텐츠 처리**
  - 빈 HTML 페이지 수집
  - 적절한 에러 처리 또는 빈 document 저장 확인

**테스트:**
```bash
docker-compose up -d
pytest tests/integration/scenarios/test_failure_flows.py -v
```

**커밋 메시지:**
```
test: add integration tests for failure scenarios
```

---

### Task 8: Integration Test - Edge Cases

**작업 내용:**
- [x] `tests/integration/scenarios/test_edge_cases.py` 작성:
  
  **시나리오 1: 매우 긴 URL**
  - 극단적으로 긴 URL 입력
  - 적절한 처리 (성공 또는 명확한 에러) 확인
  
  **시나리오 2: 특수 문자가 포함된 URL**
  - URL에 한글, 공백, 특수문자 포함
  - URL encoding이 올바르게 처리되는지 확인
  
  **시나리오 3: 매우 큰 HTML 페이지**
  - 10MB 이상의 큰 HTML 콘텐츠
  - 메모리 오버플로우 없이 정상 처리되는지 확인
  
  **시나리오 4: Redirect 처리**
  - 301/302 리다이렉트가 있는 URL
  - 최종 URL로 정상 수집되는지 확인
  
  **시나리오 5: 동시 다발적 요청 (Concurrency)**
  - 여러 개의 ingestion 요청을 동시에 보내기
  - 모든 Job이 독립적으로 정상 처리되는지 확인
  - Job ID 충돌이 없는지 확인

**테스트:**
```bash
docker-compose up -d
pytest tests/integration/scenarios/test_edge_cases.py -v
```

**커밋 메시지:**
```
test: add integration tests for edge cases
```

---

### Task 9: Integration Test - Dependency Injection 검증

**작업 내용:**
- [x] `tests/integration/test_dependency_injection.py` 작성:
  - FastAPI dependencies가 올바른 객체 반환하는지 검증
  - `get_neo4j_storage()`, `get_chroma_storage()`, `get_composite_storage()` 테스트
  - 실제 환경 변수 기반으로 인프라 컴포넌트 초기화 검증

**테스트:**
```bash
pytest tests/integration/test_dependency_injection.py -v
```

**커밋 메시지:**
```
test: add dependency injection container verification tests
```

---

### Task 10: 전체 테스트 실행 및 검증

**작업 내용:**
- [x] 모든 기존 테스트 통과 확인
- [x] 새로운 Contract Tests 통과 확인
- [x] Integration Tests 통과 확인

**테스트:**
```bash
# 전체 테스트 실행
pytest -v

# Contract Tests만 실행
pytest tests/contracts/ -v

# Integration Tests만 실행
pytest tests/integration/ -v
```

**커밋 메시지:**
```
test: verify all tests pass with new testing infrastructure
```

---

### Task 11: PR 준비 및 문서화

**작업 내용:**
- [x] `specs/009-testing-strategy/walkthrough.md` 작성
- [x] `specs/009-testing-strategy/pr_description.md` 작성
- [x] 모든 변경사항 커밋 및 푸시

**테스트:**
```bash
# CI 파이프라인에서 자동 실행
git push origin feature/testing-strategy-improvement
```

**커밋 메시지:**
```
docs: add walkthrough and PR description for testing strategy improvement
```

---

## ✅ 검증 계획 (Verification Plan)

### 1. 자동화된 테스트 (Automated Tests)

#### Contract Tests
```bash
# 모든 Contract Tests 실행
pytest tests/contracts/ -v

# 개별 실행
pytest tests/contracts/test_storage_contract.py -v
pytest tests/contracts/test_job_repository_contract.py -v
pytest tests/contracts/test_llm_contract.py -v
pytest tests/contracts/test_scraper_contract.py -v
```

**기대 결과:**
- 모든 인터페이스-구현체 쌍이 계약을 준수함
- 생성자 시그니처 불일치 즉시 감지

#### Integration Tests
```bash
# Docker Compose로 실제 DB 환경 실행
docker-compose up -d

# E2E 시나리오 테스트
pytest tests/integration/scenarios/test_full_ingestion_flow.py -v

# DI Container 검증
pytest tests/integration/test_dependency_injection.py -v
```

**기대 결과:**
- 실제 런타임 환경에서 전체 플로우 정상 동작
- Job 상태 전이 (PENDING → RUNNING → COMPLETED) 검증
- DI Container가 올바른 객체 주입

#### 전체 테스트 스위트
```bash
# 모든 테스트 실행
pytest -v --tb=short

# 커버리지 포함 (선택적)
pytest --cov=app --cov-report=term-missing
```

**기대 결과:**
- 기존 테스트 포함 모든 테스트 통과
- 새로운 테스트들이 CI 파이프라인에서 정상 실행

### 2. 수동 검증 (Manual Verification)

#### 문서 검토
- [x] `docs/testing_strategy.md` 가독성 확인
- [x] 테스트 전략이 명확히 이해 가능한지 확인

#### CI 파이프라인 확인
- [x] GitHub Actions에서 모든 테스트 통과 확인
- [x] CI 실행 시간이 허용 범위 내인지 확인 (목표: 5분 이내)

---

## 🔧 기술 스택 (Tech Stack)

- **Testing Framework:** pytest 8.4.2
- **Contract Testing:** Python Protocol (typing.Protocol)
- **Integration Testing:** FastAPI TestClient, pytest fixtures
- **Optional:** testcontainers-python (향후 Testcontainers 도입 시)

---

## 📊 예상 영향 (Expected Impact)

### 긍정적 효과
- ✅ 인터페이스 변경 시 구현체 불일치 자동 감지
- ✅ 통합 환경 버그를 테스트 단계에서 조기 발견
- ✅ 리팩토링 안전성 증가
- ✅ 테스트 전략 문서화로 팀 전체 품질 향상

### Trade-offs
- ⚠️ 초기 테스트 인프라 구축 시간 소요 (예상: 4-6시간)
- ⚠️ CI 파이프라인 실행 시간 약간 증가 (예상: +1-2분)

---

## 🚨 리스크 및 대응 (Risks & Mitigation)

### Risk 1: Integration Test 실행 시간 증가
- **대응:** 실제 DB 사용이 필요한 테스트만 Integration으로 분류
- **대응:** Docker Compose 병렬 실행으로 시간 단축

### Risk 2: Contract Test 유지보수 부담
- **대응:** 인터페이스 변경 시 Contract Test도 함께 업데이트하는 규칙 수립
- **대응:** 명확한 에러 메시지로 수정 지점 즉시 파악 가능

---

## 📚 참고 문서 (References)

- `constitution.md` - 프로젝트 헌법
- `agent.md` - Agent 행동 규칙
- `specs/testing-strategy-improvement/spec.md` - 요구사항 명세
- [Testing Pyramid - Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
