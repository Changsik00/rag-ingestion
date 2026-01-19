# Walkthrough: System Stability & Test Refactoring (Spec 018)

## 🎯 Goal
To improve system reliability by establishing a robust exception handling hierarchy, standardized logging, and restoring critical integration tests.

## 🏗️ Changes

### 1. Custom Exception Hierarchy (`app/core/exceptions.py`)
Implemented a unified exception base `DoitException` and specific subclasses:
- `DomainException`: Business logic violations.
- `InfrastructureException`: External system failures (DB, API).
- `ScrapingError`, `LLMError`, `DatabaseError`.

### 2. Standardized Logging (`app/core/logging_config.py`)
Replaced `print()` with structured logging via `setup_logger`, ensuring consistent formats and severities.

### 3. Storage Hardening (`app/infrastructure/storage/`)
- **Neo4jStorage**: Added `InfrastructureException` wrapping and fixed context manager buffering in tests.
- **ChromaStorage**: Added null checks for `get()` to prevent `IndexError` on empty results.

### 4. Test Restoration & Refactoring
Restored skipped tests and fixed anti-patterns:
- **`test_failure_flows.py`**: Fixed `test_llm_failure_still_saves_document` using `app.dependency_overrides` with manual `IngestionService` injection to reliably mock LLM failures.
- **`test_entity_relationships.py`**: Refactored to use `TestClient` and mocks, removing external `requests` dependencies.
- **`test_scraper.py`**: Replaced broad `try-except` with `pytest.raises(requests.exceptions.HTTPError)`.
- **`test_storage.py`**: Fixed unit tests by using `MagicMock` for Neo4j context managers.

## 🧪 Verification Results

### Automated Tests
Ran `uv run pytest -v` (107 Tests Passed).
- Unit Tests: Verified exception mapping and mock interactions.
- Integration Tests: Verified full ingestion flows, failure handling (LLM fail -> Job Completed), and entity extraction.

### Manual Verification
- Confirmed `test_llm_failure_still_saves_document` properly simulates "Partial Success" (Scrape OK, LLM Fail -> Save Document) without crashing the job.
