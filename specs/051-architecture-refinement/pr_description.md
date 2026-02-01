# refactor: architecture refinement and api standardization (spec 051)

## 📌 Summary
Refactored the AI infrastructure, standardized naming conventions (State, Agent, DTO), unified all API paths under `/v1/` (removing `/admin/`), and enforced Clean Architecture boundaries.

## 🛠 Key Changes

### 1. AI Infrastructure Consolidation
- **New Hierarchy**: `app/infrastructure/ai/{extractors, orchestrators, nodes, graphs}`
- **Moved & Renamed**:
  - `LangChainLLMAdapter` -> `LangChainExtractor`
  - `LangGraphAdapter` -> `IngestionOrchestrator`
  - `IngestionState` -> `IngestionGraphState`
  - `AdminAgent` -> `ConversationalRAGAgent`

### 2. Domain & Layer Refactoring
- **Repositories**: Renamed `infrastructure/storage` -> `infrastructure/repositories`
- **DTOs**: Renamed `interfaces/api/schemas` -> `interfaces/api/dto`
- **Core Utils**: Moved `domain/services/file_processor.py` -> `core/utils/file_processor.py`
- **Value Objects**: Introduced `DocumentMetadata` and `Chunk` VOs.

### 3. API Path Standardization & Refinement
- **Unified Paths**: All endpoints now under `/v1/` (e.g., `/v1/ingest/web`).
- **Removed Admin Prefix**: Eliminated `/admin/` from all API routes.
- **Centralized Router**: Consolidated all version 1 routers into `app/interfaces/api/v1/endpoints/`.
- **DI Fixes**: Resolved logic errors in `dependencies.py` and updated DI tests to zero-argument `get_repository()`.

### 4. Code Quality & Verification
- **Linting**: Fixed 40+ ruff errors.
- **Testing**: 194 Tests Passed (Unit & Integration).
- **Docker**: Updated `ADMIN_API_URL` to match new path structure.

## ✅ Verification
- [x] `uv run pytest` passed (194 passed, 60 skipped).
- [x] `uv run ruff check .` passed (0 errors).
- [x] Manual verification of Admin UI connectivity and DI logic.

## 📝 Impact
- Breaking changes for any external scripts importing from `app.infrastructure.brain` or `app.infrastructure.llm`.
- Database schemas (Neo4j/Chroma) remain compatible (naming changes were code-only).
