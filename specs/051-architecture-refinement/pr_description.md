# PR: Architecture Refinement (Spec 051)

## 📌 Summary
Refactored the AI infrastructure to a hierarchical structure, standardized naming conventions (State, Agent, DTO), and enforced Clean Architecture boundaries by moving utilities and renaming layers.

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

### 3. Code Quality & Standardization
- **Linting**: Fixed 40+ ruff errors (imports, whitespace, undefined variables).
- **Testing**: 190 Tests Passed (Unit & Integration).
- **Dependency Injection**: Fixed logic errors in `dependencies.py` preventing app startup.

## ✅ Verification
- [x] `uv run pytest` passed (190 passed, 64 skipped).
- [x] `uv run ruff check .` passed (0 errors).
- [x] Manual verification of `dependencies.py` logic.

## 📝 Impact
- Breaking changes for any external scripts importing from `app.infrastructure.brain` or `app.infrastructure.llm`.
- Database schemas (Neo4j/Chroma) remain compatible (naming changes were code-only).
