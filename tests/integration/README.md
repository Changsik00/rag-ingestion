# Integration Tests

이 디렉토리는 시스템의 통합 테스트를 포함합니다. 실제 인프라(Neo4j, ChromaDB, Redis)와의 상호작용을 검증하며, BDD(Behavior Driven Development) 스타일의 시나리오 테스트를 포함합니다.

## Infrastructure
통합 테스트는 `conftest.py`에 정의된 픽스처를 통해 인프라 상태를 관리합니다.

### 주요 픽스처
- **`check_infrastructure`**: 테스트 실행 전 필수 서비스(Neo4j, Chroma, Redis, LLM API)의 가용성을 확인합니다. 연결할 수 없는 경우 해당 테스트를 `skip` 합니다.
- **`seed_test_data`**: 테스트 세션(scope="session") 시작 시 초기 데이터(테스트용 Document, Entity 등)를 DB에 seed 합니다. 테스트가 종료되어도 데이터는 유지될 수 있으므로, 테스트 코드 내에서 정리(cleanup) 로직이 필요할 수 있습니다.
- **`client`**: `FastAPI`의 `TestClient`를 제공합니다.

## Directory Structure
- **`bdd/`**: 시나리오 기반 통합 테스트 (e.g., `test_knowledge_graph.py`, `test_rag_service.py`)
- **`tdd/`**: (Legacy) API 단위 테스트
- **`conftest.py`**: 공통 픽스처 및 설정

## Mocking
외부 API(예: LLM, Web Scraper) 호출이 비용이나 시간 문제로 부담스러운 경우, `unittest.mock`을 사용하여 의존성을 격리합니다.
- **MockScraper**: 실제 웹 요청 없이 HTML/Markdown 응답을 시뮬레이션 (`test_edge_cases.py` 등)
- **MockLLM**: LLM API 호출 없이 JSON 응답을 시뮬레이션 (`test_intent_routing.py` 등)

## Running Tests
```bash
# 전체 통합 테스트 실행
uv run pytest tests/integration

# 특정 시나리오 실행
uv run pytest tests/integration/bdd/test_knowledge_graph.py

# 인프라가 없는 경우 (자동으로 스킵됨)
# SKIPPED [100%]
```

---

## 📖 Use Cases & BDD Scenarios

이 섹션은 BDD 시나리오의 배경이 되는 주요 사용자 스토리를 정의합니다.

### Use Case 1: 웹 콘텐츠 수집 및 저장
**Goal:** 웹 페이지를 수집하여 RAG 시스템에 저장

**Main Success Scenario:**
1. 사용자가 유효한 URL과 함께 `POST /ingest/web` 요청
2. 시스템이 Job을 생성하고 `202 Accepted` 반환
3. Background에서 웹 페이지 스크래핑
4. LLM을 통한 메타데이터 추출 (enable_extraction=True)
5. Neo4j와 ChromaDB에 저장
6. Job 상태가 `COMPLETED`로 변경되고, `GET /documents`로 확인 가능

**Alternative Flows:**
- 잘못된 URL 형식 → `400/422` 반환
- 존재하지 않는 URL (404) → Job `FAILED`

### Use Case 2: 예외 상황 처리
**Goal:** 시스템이 다양한 예외 상황을 적절히 처리하는지 검증

**Scenarios:**
- **잘못된 입력**: 422 Unprocessable Entity
- **외부 리소스 실패**: Job FAILED, 상세 error_message 제공
- **Edge Cases**: 한글/특수문자 URL, 긴 URL 등 처리

### Use Case 3: 동시성 및 확장성
**Goal:** 동시 요청 처리 및 Job ID 고유성 보장

**Scenario:**
- 여러 사용자가 동시에 수집 요청 시 Job ID가 충돌하지 않고 모두 독립적으로 처리되어야 함.
