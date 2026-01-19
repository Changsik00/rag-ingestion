# Plan: System Stability & Test Refactoring (Spec 018)

## 📋 Branch Strategy
- `feature/018-system-stability`

## 🛑 User Review Required
> [!IMPORTANT]
> **Exception Hierarchy Change**: 기존에 `Exception`으로 퉁치던 에러들이 세분화됩니다 (`DomainException`, `InfrastructureException`). 상위 레벨에서 특정 에러를 핸들링하던 로직이 있다면 영향받을 수 있습니다.

## 🎯 Core Strategy
**"Test First, Fix Later"**: 모든 수정 작업은 테스트(Unit Test 수정 including) -> 실패 확인 -> 구현 -> 성공 확인 순서로 진행합니다. 특히 기존에 Skip된 테스트들은 "왜 실패하는지"를 문서화하고 수정합니다.

## 📂 Proposed Changes

### 1. Core Improvements
#### [NEW] [exceptions.py](file:///Users/ck/Project/doit/rag-ingestion/app/core/exceptions.py)
*   **Purpose**: 어플리케이션 전역에서 사용할 커스텀 예외 계층 정의.
*   `DoitException(Exception)` (Base)
*   `DomainException` / `InfrastructureException`

#### [NEW] [logging_config.py](file:///Users/ck/Project/doit/rag-ingestion/app/core/logging_config.py)
*   **Purpose**: 표준 로깅 설정.
*   `setup_logger()` 함수 제공.

### 2. Infrastructure Layer Hardening
#### [MODIFY] [neo4j_document_repository.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j_document_repository.py)
*   `get()`: `result.single()` 결과가 None일 때 명시적 처리.
*   `save()`: `try-except` 블록 추가 -> `InfrastructureException` 래핑.

#### [MODIFY] [chroma.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/chroma.py)
*   `get()`: Collection 조회 결과 검증 강화.

### 3. Application Layer Refactoring
#### [MODIFY] [ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/use_cases/ingestion.py)
*   `try-except Exception` 제거.
*   `process_job()` 내에서 구체적 예외(`ScrapingError`, `LLMError`) 별로 처리.
*   `print()` 문을 `logger`로 교체.

### 4. Test Restoration
#### [MODIFY] [test_scraper.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/test_scraper.py)
*   `try-except` assertion 제거하고 `pytest.raises` 사용.

#### [MODIFY] [test_failure_flows.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/bdd/test_failure_flows.py)
*   `test_llm_failure_still_saves_document` Skip 제거 및 Mocking 수정.

#### [MODIFY] [test_entity_relationships.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/bdd/test_entity_relationships.py)
*   `test_scenario_1...` Skip 제거 및 유효한 URL(httpbin 등) 사용.

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (Core & Exceptions)
uv run pytest tests/unit -v

# Integration Tests (Full Flow)
uv run pytest tests/integration -v
```

### Manual Verification
1. `docker-compose up -d`
2. `curl -X POST /ingest/web ...` 실행
3. `docker-compose logs backend`에서 JSON 또는 포맷팅된 로그 확인.
