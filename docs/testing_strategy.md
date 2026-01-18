# Testing Strategy Guide

이 문서는 프로젝트의 테스트 전략 및 원칙을 정의합니다. 모든 Spec 작업 시 이 가이드를 참조하여 품질 높은 테스트를 작성해야 합니다.

---

## 📌 테스트 철학 (Testing Philosophy)

### 왜 테스트가 중요한가?

**Spec 008에서 발견된 문제:**
- `Neo4jStorage` 생성자 파라미터 불일치 → 통합 환경에서만 발견
- Import 오류 → 모듈 구조 변경 시 단위 테스트에서 감지 못함
- DI Container 실패 → Mock 환경과 실제 환경의 불일치

**근본 원인:**
- 단위 테스트의 User Case Coverage 부족
- Interface-Implementation 계약 검증 부재
- 실제 런타임 환경을 재현하는 Integration Test 시나리오 부족

**목표:**
> **"통합 환경에서만 발견되는 버그를 테스트 단계에서 조기 발견한다"**

---

## 🧪 TDD vs BDD

### TDD (Test-Driven Development)

**목적:** 기능이 의도대로 동작하는지 검증

**특징:**
- 개발자 관점의 테스트
- 함수/메서드 레벨의 단위 검증
- 빠른 피드백 루프
- Mock 사용 가능

**적용:**
- Unit Tests (개별 함수, 클래스)
- Contract Tests (인터페이스 준수 여부)

**예시:**
```python
def test_scraper_extracts_title_from_html():
    """주어진 HTML에서 title을 정확히 추출한다"""
    scraper = BasicScraper()
    html = "<html><head><title>Test Page</title></head></html>"
    
    result = scraper.scrape(html)
    
    assert result.title == "Test Page"
```

---

### BDD (Behavior-Driven Development)

**목적:** 사용자 관점에서 시스템이 어떻게 행동하는지 검증

**특징:**
- 사용자 관점의 시나리오 테스트
- Given-When-Then 구조
- **예외 상황 집중** ⭐
- 실제 환경 사용

**적용:**
- Integration Tests (실제 사용자 시나리오)
- E2E Tests (전체 워크플로우)

**예시:**
```python
def test_user_submits_invalid_url_should_return_clear_error():
    """
    Given: 사용자가 잘못된 URL 형식을 입력하고
    When: 웹 수집 요청을 보내면
    Then: 400 Bad Request와 명확한 에러 메시지를 받는다
    """
    # Given
    invalid_url = "not-a-valid-url"
    
    # When
    response = client.post("/ingest/web", json={"url": invalid_url})
    
    # Then
    assert response.status_code == 400
    assert "Invalid URL format" in response.json()["detail"]
```

---

### 언제 무엇을 사용할까?

| 테스트 타입 | 접근 방식 | 우선순위 | 목적 |
|------------|----------|---------|------|
| **Unit Tests** | TDD | 기본 | 기능이 정상 동작하는지 검증 |
| **Contract Tests** | TDD | 높음 | 인터페이스-구현체 계약 검증 |
| **Integration Tests** | **BDD** | **최우선** | **예외 상황 검증** ⭐ |
| **E2E Tests** | BDD | 선택적 | 전체 워크플로우 검증 |

---

## 🏗 테스트 피라미드

```
                    /\
                   /  \  E2E Tests (적음, 느림, 실제 환경)
                  /____\
                 /      \  Integration Tests (중간, API + 실제 DB)
                /________\
               /          \
              /____________\  Unit Tests (많음, 빠름, 격리된 환경)
```

### 각 레벨의 역할

#### 1. Unit Tests (Base)
- **비중:** 60-70%
- **속도:** 매우 빠름 (ms 단위)
- **목적:** 개별 함수/클래스의 로직 검증
- **환경:** Mock, Stub 사용
- **예시:**
  - `test_extractor_parses_metadata()`
  - `test_scraper_extracts_title()`

#### 2. Integration Tests (Middle) ⭐
- **비중:** 25-35%
- **속도:** 중간 (초 단위)
- **목적:** **실제 사용자 시나리오 및 예외 상황 검증**
- **환경:** 실제 DB, 실제 API (Docker Compose)
- **예시:**
  - `test_user_submits_invalid_url()` (BDD)
  - `test_job_fails_when_url_404()` (BDD)
  - `test_concurrent_ingestion_requests()` (BDD)

#### 3. E2E Tests (Top)
- **비중:** 5-10%
- **속도:** 느림 (분 단위)
- **목적:** 전체 시스템 워크플로우 검증
- **환경:** 완전한 프로덕션 환경 복제
- **예시:**
  - Playwright를 사용한 Admin Dashboard UI 테스트
  - 외부 API 연동 테스트

---

## 🤝 Contract Testing

### 개념

**Contract Testing이란?**
> 인터페이스(Protocol)를 구현한 모든 클래스가 동일한 "계약"을 준수하는지 검증

**왜 필요한가?**
- Spec 008에서 `Neo4jStorage`와 `ChromaStorage`의 생성자가 달랐음
- Python Protocol은 런타임에만 검증됨
- 정적 타입 체커(mypy)로도 놓치는 부분이 있음

### 구현 방법

```python
# tests/contracts/test_storage_contract.py
import pytest
from app.domain.interfaces.document_repository import DocumentRepository
from app.infrastructure.storage.neo4j import Neo4jStorage
from app.infrastructure.storage.chroma import ChromaStorage

@pytest.fixture(params=[
    Neo4jStorage,
    ChromaStorage,
])
def storage_class(request):
    """모든 DocumentRepository 구현체를 parametrize"""
    return request.param

def test_storage_implements_document_repository(storage_class):
    """모든 Storage는 DocumentRepository를 구현해야 함"""
    assert issubclass(storage_class, DocumentRepository)

def test_storage_has_save_method(storage_class):
    """모든 Storage는 save 메서드를 가져야 함"""
    assert hasattr(storage_class, 'save')
    assert callable(getattr(storage_class, 'save'))

def test_storage_has_get_method(storage_class):
    """모든 Storage는 get 메서드를 가져야 함"""
    assert hasattr(storage_class, 'get')
    assert callable(getattr(storage_class, 'get'))
```

### Contract Tests 작성 원칙

1. **모든 인터페이스에 대해 작성**
   - `DocumentRepository`, `JobRepository`, `LLM`, `Scraper`

2. **Parametrize 사용**
   - 같은 테스트를 모든 구현체에 대해 실행

3. **메서드 시그니처 검증**
   - 메서드 존재 여부
   - 파라미터 개수 및 타입

4. **예외 처리 일관성**
   - 같은 상황에서 같은 예외 발생

---

## 🔗 Integration Test 전략

### 원칙

**Integration Tests는 BDD 중심으로 작성한다!**

| 구분 | 비중 | 중요도 |
|-----|------|--------|
| 성공 케이스 | 20% | 당연함 (TDD로도 커버) |
| **예외 케이스** | **60%** | **최우선** ⭐ |
| Edge Cases | 20% | 중요함 |

### 성공 시나리오 (Success Cases)

**목적:** 기본 플로우가 정상 동작하는지 검증

**예시:**
```python
def test_successful_web_ingestion_stores_document():
    """
    Given: 유효한 URL과 함께 수집 요청을 보내고
    When: Job이 완료되면
    Then: Document가 Neo4j와 ChromaDB에 저장된다
    """
    # Given
    url = "https://example.com/article"
    
    # When
    response = client.post("/ingest/web", json={
        "url": url,
        "enable_extraction": True
    })
    job_id = response.json()["job_id"]
    
    # Then - Job 완료 대기
    wait_for_job_completion(job_id)
    
    # Then - Document 저장 확인
    docs_response = client.get("/documents")
    assert len(docs_response.json()) > 0
    assert any(doc["source"]["url"] == url for doc in docs_response.json())
```

---

### 예외 시나리오 (Failure Cases) ⭐

**목적:** 시스템이 예외 상황을 어떻게 처리하는지 검증

**커버해야 할 케이스:**

#### 1. 잘못된 입력 (Client Error)
```python
def test_invalid_url_format_returns_400():
    """
    Given: 잘못된 URL 형식을 입력하고
    When: 수집 요청을 보내면
    Then: 400 에러와 명확한 메시지를 반환한다
    """
    response = client.post("/ingest/web", json={"url": "not-a-url"})
    
    assert response.status_code == 400
    assert "Invalid URL" in response.json()["detail"]
```

#### 2. 외부 의존성 실패 (404, Network Error)
```python
def test_url_404_fails_job_with_clear_error():
    """
    Given: 존재하지 않는 URL로 수집 요청하고
    When: Job이 실행되면
    Then: Job이 FAILED 상태로 전이되고 에러 메시지를 포함한다
    """
    response = client.post("/ingest/web", json={
        "url": "https://example.com/non-existent"
    })
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "FAILED"
    assert "404" in job.get("error", "")
```

#### 3. LLM API 실패 (Mock)
```python
def test_llm_failure_still_saves_document(mocker):
    """
    Given: LLM API가 실패하는 상황에서
    When: 수집 요청을 보내면
    Then: Document는 저장되지만 metadata는 비어있다
    """
    # LLM Mock으로 에러 발생시키기
    mocker.patch('app.core.llm.get_llm', side_effect=Exception("API quota exceeded"))
    
    response = client.post("/ingest/web", json={"url": "https://example.com"})
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    # Document는 저장되었지만 metadata 없음
    docs = client.get("/documents").json()
    assert len(docs) > 0
    assert docs[0]["metadata"] is None or docs[0]["metadata"] == {}
```

#### 4. 동시성 문제 (Concurrency)
```python
def test_concurrent_requests_handled_independently():
    """
    Given: 여러 수집 요청을 동시에 보내고
    When: 모든 Job이 실행되면
    Then: 각 Job이 독립적으로 처리되고 ID 충돌이 없다
    """
    urls = [f"https://example.com/page{i}" for i in range(5)]
    
    # 동시 요청
    responses = [
        client.post("/ingest/web", json={"url": url})
        for url in urls
    ]
    
    job_ids = [r.json()["job_id"] for r in responses]
    
    # 모든 Job ID가 고유함
    assert len(set(job_ids)) == 5
    
    # 모든 Job이 완료됨
    for job_id in job_ids:
        wait_for_job_completion(job_id)
        job = client.get(f"/jobs/{job_id}").json()
        assert job["status"] in ["COMPLETED", "FAILED"]
```

---

### Edge Cases

**목적:** 극단적인 상황에서도 시스템이 안정적인지 검증

**예시:**
- 매우 긴 URL (1000자+)
- 특수 문자가 포함된 URL (한글, 공백, 이모지)
- 매우 큰 HTML 페이지 (10MB+)
- Redirect 체이닝 (301 → 302 → 200)

---

## 📋 Spec별 테스트 체크리스트

새로운 Spec을 구현할 때마다 다음을 확인하세요:

### 필수 항목

- [ ] **Contract Tests 작성**
  - 새로운 인터페이스를 추가했다면 Contract Test 작성
  - 기존 인터페이스에 구현체를 추가했다면 parametrize에 추가

- [ ] **Unit Tests (TDD)**
  - 새로운 함수/클래스의 기본 동작 검증
  - Mock을 사용한 빠른 테스트

- [ ] **Integration Tests (BDD)**
  - [ ] 성공 시나리오 1개 이상
  - [ ] **예외 시나리오 3개 이상** ⭐
  - [ ] Edge Case 1개 이상

- [ ] **CI 통과**
  - 모든 테스트 통과
  - Ruff linter 통과

### 선택 항목

- [ ] E2E Tests (Playwright)
  - UI가 변경된 경우에만

---

## 🏭 Fixture 및 Mock 전략

### 실제 DB vs Mock

| 테스트 타입 | Neo4j | ChromaDB | LLM | 이유 |
|------------|-------|----------|-----|------|
| Unit Tests | Mock | Mock | Mock | 빠른 피드백 |
| Contract Tests | Mock | Mock | Mock | 인터페이스 검증만 |
| Integration Tests | **실제** | **실제** | Mock | 런타임 검증 |
| E2E Tests | 실제 | 실제 | 실제 | 전체 검증 |

### Pytest Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def docker_services():
    """Docker Compose로 실제 DB 시작"""
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    yield
    subprocess.run(["docker-compose", "down"], check=True)

@pytest.fixture
def client(docker_services):
    """실제 DB와 연동된 TestClient"""
    from app.interfaces.api.main import app
    return TestClient(app)
```

---

## 🚀 CI/CD 테스트 전략

### GitHub Actions 파이프라인

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit -v
      
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/contracts -v
      
  integration-tests:
    runs-on: ubuntu-latest
    services:
      neo4j: ...
    steps:
      - run: docker-compose up -d
      - run: pytest tests/integration -v
```

### 실행 순서

1. **Unit Tests** (가장 빠름, 항상 실행)
2. **Contract Tests** (빠름, 항상 실행)
3. **Integration Tests** (중간, PR 시 실행)
4. **E2E Tests** (느림, main 머지 전 실행)

---

## 📚 참고 자료

### External Resources
- [Testing Pyramid - Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Contract Testing - Pact](https://docs.pact.io/)
- [Python Protocol (PEP 544)](https://peps.python.org/pep-0544/)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

### Related Documentation
- [Architecture Guide](./architecture.md) - Clean Architecture layer separation principles

---

## 🔄 이 문서의 업데이트

이 문서는 프로젝트가 진화함에 따라 지속적으로 업데이트됩니다.

**마지막 업데이트:** 2026-01-19 (Spec 015: Documentation Update)  
**작성일:** 2026-01-17 (Spec 009: Testing Strategy)

