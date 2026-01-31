# Task List: Spec-051 (Hierarchical AI Structure)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: P1 - Core Domain & Naming (High)
### 1-1. Value Objects
- [x] **Create**: `app/domain/value_objects/chunk.py` (Pydantic VO)
- [x] **Create**: `app/domain/models/document_metadata.py` (Pydantic VO)
- [x] **Refactor**: Update `Document` to use new VOs
- [x] **Delete**: `app/domain/entities/chunk.py`
- [x] **Commit**: `refactor(domain): introduce DocumentMetadata and Chunk VOs (Spec 051)`

### 1-2. Interfaces
- [x] **Create**: `app/domain/interfaces/chunker.py` (Protocol)
- [x] **Refactor**: `app/infrastructure/chunker/langchain_chunker.py` (Implement Protocol)
- [x] **Commit**: `refactor(domain): introduce Chunker protocol (Spec 051)`

### 1-3. Semantic Renaming
- [x] **Rename**: `IntegrityService` -> `Integrity`
- [x] **Rename**: `FeedbackService` -> `Feedback`
- [x] **Rename**: `IngestionService` -> `IngestionUseCase`
- [x] **Commit**: `refactor(service): rename services to domain concepts (Spec 051)`

## Task 2: P2 - AI Consolidaton & Cleanup (Medium)
### 2-1. AI Hierarchy Setup
- [x] **Create Dirs**: `app/infrastructure/ai/{extractors,orchestrators,nodes,graphs}`
- [x] **Commit**: `chore(infra): setup hierarchical ai folder structure (Spec 051)`

### 2-2. Move & Rename (LLM/Brain -> AI)
- [x] **Move**: `infrastructure/llm/langchain_adapter.py` -> `ai/extractors/langchain_extractor.py`
- [x] **Move**: `infrastructure/brain/adapter.py` -> `ai/orchestrators/ingestion_orchestrator.py`
- [x] **Move**: `infrastructure/brain/nodes.py` -> `ai/nodes/ingestion_nodes.py`
- [x] **Move**: `infrastructure/brain/graph.py` -> `ai/graphs/ingestion_graph.py`
- [x] **Delete**: `infrastructure/llm`, `infrastructure/brain` folders
- [x] **Refactor**: Update all imports to use new paths (Global Find & Replace)
- [x] **Commit**: `refactor(infra): consolidate ai modules into hierarchy (Spec 051)`

### 2-3. Admin Agent (Consolidate)
- [x] **Refactor**: Ensure `AdminAgent` uses `IngestionOrchestrator` if applicable
- [x] **Move**: `infrastructure/brain/logic.py` -> `ai/nodes/logic.py`
- [x] **Commit**: `refactor(admin): update admin agent dependencies (Spec 051)`

### 2-4. Repositories
- [x] **Rename Dir**: `infrastructure/storage` -> `infrastructure/repositories`
- [x] **Refactor**: Update all imports `app.infrastructure.storage` -> `app.infrastructure.repositories`
- [x] **Commit**: `refactor(infra): rename storage to repositories (Spec 051)`

### 2-5. Generic Utils (Core)
- [x] **Move**: `domain/services/file_processor.py` -> `core/utils/file_processor.py`
- [x] **Commit**: `refactor(core): move file_processor to core utils (Spec 051)`

## Task 3: P3 - Standardization (Low)
### 3-1. State & Agent
- [x] **Rename**: `IngestionState` -> `IngestionGraphState`
- [x] **Rename**: `RAGState` -> `RAGGraphState`
- [x] **Rename**: `AdminAgent` -> `ConversationalRAGAgent`
- [x] **Commit**: `refactor(std): standardize state and agent names (Spec 051)`

### 3-2. DTO
- [x] **Rename Dir**: `interfaces/api/schemas` -> `interfaces/api/dto`
- [x] **Refactor**: All imports
- [x] **Commit**: `refactor(api): rename schemas to dto (Spec 051)`

### 3-3. API Path Unification (Spec 051)
- [x] **Consolidate**: Move all v1 routers to `v1/endpoints/`
- [x] **Standardize**: Remove `/admin/` prefix from all paths
- [x] **Prefix**: Use `/v1/` for all endpoints centrally in `main.py`
- [x] **Frontend**: Update Streamlit pages to use new paths
- [x] **Commit**: `refactor(api): unify paths under /v1 and remove /admin (Spec 051)`

---

## Task N: PR Creation & Archiving
- [x] Code Quality Check: `uv run ruff check .`
- [x] Test: `uv run pytest`
- [x] Documentation: Walkthrough & PR Description
- [x] Archive Commit: `docs(spec-051): archive walkthrough and pr description`
- [x] Create PR
