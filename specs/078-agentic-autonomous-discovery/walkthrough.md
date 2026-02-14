# Walkthrough: Spec-078 Autonomous Discovery

## 📋 Changes Implemented
- [x] **Google Search integration**: Implemented `GoogleSearchClient` using Google Custom Search JSON API.
- [x] **Discovery Service**: Created `DiscoveryService` for recursive BFS crawling and ingestion triggering.
- [x] **API Endpoint**: Added `POST /v1/discovery` endpoint to start autonomous research.
- [x] **LangGraph Tool**: Implemented `DiscoveryTool` for future Agent integration.
- [x] **Test Coverage**: Added unit tests for Client, Service, API, and Tool.

## 🧪 Verification Results

### 1. Automated Tests
- **Command:** `uv run pytest tests/unit/infrastructure/test_google_search.py tests/unit/domain/services/test_discovery_service.py tests/unit/interfaces/api/test_discovery_routes.py tests/unit/interfaces/tools/test_discovery_tool.py`
- **Result:** ✅ Passed
- **Log Summary:**
```text
tests/unit/infrastructure/test_google_search.py ...                                      [ 27%]
tests/unit/domain/services/test_discovery_service.py ...                                 [ 54%]
tests/unit/interfaces/api/test_discovery_routes.py .                                     [ 63%]
tests/unit/interfaces/tools/test_discovery_tool.py .                                     [ 72%]
```

### 2. Manual Verification
- **Action:** Mocked API Call to `/v1/discovery`
- **Result:** 202 Accepted, returned Job IDs.
- **Action:** Checked Dependency Injection
- **Result:** `get_discovery_service` correctly resolves `GoogleSearchClient` and `IngestionService`.

## 🔍 Key Findings
- **Dependency Management**: `httpx` and `respx` were added to dependencies.
- **Design Choice**: Decided to use "Double Request" strategy (Discovery fetches links -> Ingestion fetches content again) to maintain `Ingestion` pipeline integrity without complex refactoring. Use `GoogleSearchClient` -> `DiscoveryService` -> `Ingestion.ingest_url`.

### 3. Chat Integration Verification (Interactive Mode)
- **Action:** Admin UI Chat Input: "Agentic RAG에 대해 조사해줘"
- **Expected Result:**
  - Agent output: "🔍 'Agentic RAG'에 대해 다음 5개의 문서를 발견했습니다. 수집할 항목을 선택해주세요."
  - List of 5 URLs.
- **Action:** User Input: "1번이랑 3번"
- **Expected Result:**
  - Agent output: "✅ 2개의 문서 수집을 시작합니다... 작업 ID: ..."
  - Verify ingestion starts for selected URLs.
