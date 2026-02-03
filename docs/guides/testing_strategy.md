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

## 🧪 테스트 계층 (Test Layers)

본 프로젝트는 **Clean Architecture** 계층과 **테스트 성격**에 따라 다음과 같이 테스트를 분류합니다.

### 1. Unit Tests (단위 테스트)
**목적:** 개별 컴포넌트의 순수 로직 검증  
**경로:** `tests/unit/`

- **`domain/`**: 엔티티 생명주기, 밸류 오브젝트 불변성, 도메인 예외 검증 (Mock 지양)
- **`application/`**: 유스케이스 로직, 서비스 오케스트레이션 검증 (Interface 기반 Mock 활용)
- **`infrastructure/`**: 어댑터 구현체, 외부 라이브러리 연동 로직 (LLM Factory, Scraper 등)
- **`interfaces/`**: API DTO 변환, 요청 유효성 검사

---

### 2. Integration Tests (통합 테스트)
**목적:** 여러 컴포넌트 및 인프라(DB, Redis 등)와의 상호작용 검증  
**경로:** `tests/integration/`

사용자의 피드백에 따라 **기술적 단위(Functional)**와 **비즈니스 시나리오(Scenarios)**로 엄격하게 분배합니다.

#### **A. Functional Tests (`functional/`)**
- **정의**: "기술적 정합성" 중심의 통합 테스트.
- **범위**: 개별 모듈이 인프라와 통신하며 의도한 기술적 명세를 충족하는지 확인.
- **예시**:
    - 리포지토리의 CRUD 동작 및 트랜잭션.
    - API 엔드포인트의 기술적 규격 (404 처리, 스키마 검증).
    - `IntentClassifier`나 `StrategySelection`과 같은 핵심 알고리즘의 기술적 정확성.

#### **B. Scenario Tests (`scenarios/`)**
- **정의**: "비즈니스 흐름" 중심의 시나리오 테스트.
- **범위**: 사용자의 가치 전달 관점에서 여러 모듈이 협력하는 전체 워크플로우를 검증.
- **예시**:
    - **Ingestion Pipeline**: URL 입력 → 스크래핑 → 청킹 → 저장까지의 전체 성공 시나리오.
    - **HITL Workflow**: 검증 실패 시 Human-in-the-loop 대기 및 재개 흐름.
    - **RAG Pipeline**: 질문 입력 → 검색 → 추론 → 답변 생성 및 출처 표시.

---

## 🛠 인프라 및 환경 격리

### Infrastructure Check Fixture
모든 통합 테스트는 `check_infrastructure` 픽스처를 통해 인프라 가동 여부를 확인하며, 준비되지 않은 경우 테스트를 자동으로 **Skip** 처리합니다.

```python
@pytest.fixture(scope="session", autouse=True)
def check_infrastructure():
    """인프라(DB, Redis 등) 연결 가능 여부 확인"""
    if not all_services_ready():
        pytest.skip("Infrastructure not ready. Run 'docker compose up -d'.")
```

### Session-based Seeding
테스트 데이터 간섭을 방지하고 실행 속도를 높이기 위해 **세션 단위 시딩**을 수행합니다.

```python
@pytest.fixture(scope="session")
def seed_test_data(check_infrastructure, api_client):
    """표준 테스트 데이터 자동 주입"""
    # 1. 시딩 여부 확인
    # 2. 필요 시 데이터 주입 (Idempotency 보장)
    return seeded_metadata
```

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

### Hybrid Integration Testing (TestClient + Mock + Real DB) ⭐

**개념:**
외부 세상과의 접점(Boundary)은 **Mocking**하여 통제하고, 내부 시스템(Application + DB)의 흐름은 **실제(Real)**로 검증하는 전략입니다.

**구성:**
- **Client:** `TestClient` (FastAPI 앱 호출)
- **External API:** `Mock` (Scraper, LLM 등 통제 불가능하거나 비용/속도 문제가 있는 외부 요소)
- **Database:** `Real` (Neo4j, Chroma 등 실제 인프라)

**장점:**
1. **Determinism (결정성):** 외부 웹사이트 변경이나 네트워크 문제로 인한 Flakiness 제거.
2. **Speed (속도):** 실제 웹 스크래핑/LLM 호출 시간을 제거하여 빠른 피드백 가능.
3. **Consistency (정합성):** 내부 로직과 데이터베이스 저장은 실제로 수행하므로 신뢰성 확보.

**예시 (`test_entity_relationships.py`):**
```python
@pytest.mark.integration
def test_hybrid_flow(client):
    """
    Mock Scraper로 고정된 데이터를 주입하고,
    실제 Service와 DB가 이를 어떻게 처리하는지 검증
    """
    # 1. External Boundary Mocking
    mock_scraper = Mock()
    mock_scraper.scrape.return_value = IngestResponse(
        url="https://example.com",
        markdown="Fixed Content for Testing..."
    )
    app.dependency_overrides[get_scraper] = lambda: mock_scraper
    
    try:
        # 2. Internal Logic Execution (Real)
        response = client.post("/ingest/web", ...)
        
        # 3. DB Verification (Real)
        # 실제 Neo4j에 데이터가 들어갔는지 확인
        stored_doc = neo4j_session.run("MATCH ...").single()
        assert stored_doc is not None
    finally:
        app.dependency_overrides = {}
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
| Integration Tests | **실제** | **실제** | **Dual Strategy** | 하단 Dual Strategy 섹션 참조 |
| E2E Tests | 실제 | 실제 | 실제 | 전체 검증 |

### LLM Dual Testing Strategy ⭐

**"Mock은 시스템을 지키고, Real은 지능을 검증한다"**

LLM을 사용하는 테스트는 목적에 따라 두 가지 전략으로 나뉩니다:

| 테스트 구분 | LLM 사용 | 목적 | 장점 | 예시 |
| :--- | :--- | :--- | :--- | :--- |
| **Pipeline/Stability Tests** | **Mock** | 시스템 흐름, 에러 핸들링, 비동기 작업 검증 | 빠름, 비용 0, 결정적(Deterministic) | `test_failure_flows.py` |
| **Quality/Logic Tests** | **Real** | 프롬프트 검증, 추출 정확도, 실제 데이터 정합성 | 실제 지능 검증, 프롬프트 변경 감지 | `test_entity_relationships.py` |

> **Best Practice:** CI/CD 파이프라인에서는 비용 문제로 주로 **Mock**을 사용하고, `Quality` 테스트는 개발 단계나 특정 릴리즈 전에 선택적으로 수행하는 것을 권장합니다.


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

**마지막 업데이트:** 2026-02-03 (Spec 054: Testing Infrastructure & Taxonomy Reorganization)  
**작성일:** 2026-01-17 (Spec 009: Testing Strategy)

