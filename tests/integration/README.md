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

## Running Tests
```bash
# 전체 통합 테스트 실행
uv run pytest tests/integration

# 특정 시나리오 실행
uv run pytest tests/integration/bdd/test_knowledge_graph.py

# 인프라가 없는 경우 (자동으로 스킵됨)
# SKIPPED [100%]
```

## mocking
외부 API(예: LLM, Web Scraper) 호출이 비용이나 시간 문제로 부담스러운 경우, `unittest.mock`을 사용하여 의존성을 격리합니다.
- **MockScraper**: 실제 웹 요청 없이 HTML/Markdown 응답을 시뮬레이션
- **MockLLM**: LLM API 호출 없이 JSON 응답을 시뮬레이션 (Intent Classification 등)
