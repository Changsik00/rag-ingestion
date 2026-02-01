# Task List: Spec-051 (Hierarchical AI Structure)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [ ] 백로그 업데이트 (Note 추가)
- [ ] User Plan Accept

---

## Task 1: P1 - Core Domain & Naming (High)
### 1-1. Value Objects
- [x] **Create**: `app/domain/value_objects/chunk.py` (Pydantic VO)
- [x] **Create**: `app/domain/models/document_metadata.py` (Pydantic VO)
- [x] **Refactor**: Update `Document` to use new VOs
- [x] **Delete**: `app/domain/entities/chunk.py`
- [x] **Commit**: `refactor(domain): introduce DocumentMetadata and Chunk VOs (Spec 051)`

### 1-2. Interfaces
- [ ] **Create**: `app/domain/interfaces/chunker.py` (Protocol)
- [ ] **Refactor**: `app/infrastructure/chunker/langchain_chunker.py` (Implement Protocol)
- [x] **Commit**: `refactor(domain): introduce Chunker protocol (Spec 051)`

### 1-3. Semantic Renaming
- [ ] **Rename**: `IntegrityService` -> `Integrity`
- [ ] **Rename**: `FeedbackService` -> `Feedback`
- [ ] **Rename**: `IngestionService` -> `IngestionUseCase`
- [ ] **Commit**: `refactor(service): rename services to domain concepts (Spec 051)`

## Task 2: P2 - AI Consolidaton & Cleanup (Medium)
### 2-1. AI Hierarchy Setup
- [ ] **Create Dirs**: `app/infrastructure/ai/{extractors,orchestrators,nodes,graphs}`
- [ ] **Commit**: `chore(infra): setup hierarchical ai folder structure (Spec 051)`

### 2-2. Move & Rename (LLM/Brain -> AI)
- [ ] **Move**: `infrastructure/llm/langchain_adapter.py` -> `ai/extractors/langchain_extractor.py`
- [ ] **Move**: `infrastructure/brain/adapter.py` -> `ai/orchestrators/ingestion_orchestrator.py`
- [ ] **Move**: `infrastructure/brain/nodes.py` -> `ai/nodes/ingestion_nodes.py`
- [ ] **Move**: `infrastructure/brain/graph.py` -> `ai/graphs/ingestion_graph.py`
- [ ] **Delete**: `infrastructure/llm`, `infrastructure/brain` folders
- [ ] **Commit**: `refactor(infra): consolidate llm and brain into ai hierarchy (Spec 051)`

### 2-3. Generic Utils
- [ ] **Move**: `domain/services/file_processor.py` -> `core/utils/file_processor.py`
- [ ] **Commit**: `refactor(core): move file_processor to core utils (Spec 051)`

### 2-4. Repositories
- [ ] **Rename Dir**: `infrastructure/storage` -> `infrastructure/repositories`
- [ ] **Rename Files**: Ensure `_repository.py` suffix
- [ ] **Commit**: `refactor(infra): rename storage to repositories (Spec 051)`

## Task 3: P3 - Standardization (Low)
### 3-1. State & Agent
- [ ] **Rename**: `IngestionState` -> `IngestionGraphState`
- [ ] **Rename**: `RAGState` -> `RAGGraphState`
- [ ] **Rename**: `AdminAgent` -> `ConversationalRAGAgent`
- [ ] **Commit**: `refactor(std): standardize state and agent names (Spec 051)`

### 3-2. DTO
- [ ] **Rename Dir**: `interfaces/api/schemas` -> `interfaces/api/dto`
- [ ] **Refactor**: All imports
- [ ] **Commit**: `refactor(api): rename schemas to dto (Spec 051)`

---

## Task N: PR Creation & Archiving
- [ ] Code Quality Check: `uv run ruff check .`
- [ ] Test: `uv run pytest`
- [ ] Documentation: Walkthrough & PR Description
- [ ] Archive Commit: `docs(spec-051): archive walkthrough and pr description`
- [ ] Create PR
