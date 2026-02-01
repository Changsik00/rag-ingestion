# Task List: Spec 052 - Clean Architecture Layer Refinement

## Progress
- [x] Spec number confirmed and branch created
- [x] spec.md written
- [x] plan.md written
- [ ] task.md written
- [ ] Backlog updated
- [ ] User plan acceptance

---

## Task 1: Interface Layer Migration (P1 - High)

### 1-1. LLM Interface to Application Layer
- [ ] **Create Dir**: `app/application/interfaces/` (if not exists)
- [ ] **Move**: `app/domain/interfaces/llm.py` → `app/application/interfaces/llm.py`
- [ ] **Find Imports**: `grep -r "from app.domain.interfaces.llm" app/ tests/`
- [ ] **Update**: All import statements (~15 files)
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(layer): move llm interface to application layer (Spec 052)`

### 1-2. Scraper Interface to Application Layer
- [ ] **Move**: `app/domain/interfaces/scraper.py` → `app/application/interfaces/scraper.py`
- [ ] **Update**: All imports (~8 files)
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(layer): move scraper interface to application layer (Spec 052)`

### 1-3. Feedback Service to Application Layer
- [ ] **Move**: `app/domain/services/feedback.py` → `app/application/services/feedback.py`
- [ ] **Move Test**: `tests/unit/domain/services/test_feedback.py` → `tests/unit/application/services/test_feedback.py` (if exists)
- [ ] **Update**: All imports (~10 files)
- [ ] **Update**: Dependency injection in `dependencies.py`
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(layer): move feedback service to application layer (Spec 052)`

---

## Task 2: Value Object Reorganization (P1 - High)

### 2-1. DocumentMetadata to Value Objects
- [ ] **Move**: `app/domain/models/document_metadata.py` → `app/domain/value_objects/document_metadata.py`
- [ ] **Update**: All imports (~20 files)
- [ ] **Cleanup**: Remove `app/domain/models/` if empty
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(vo): move DocumentMetadata to value_objects (Spec 052)`

---

## Task 3: Naming Consistency (P2 - Medium)

### 3-1. Admin Agent → Agent
- [ ] **Rename File**: `app/application/services/admin_agent.py` → `app/application/services/agent.py`
- [ ] **Rename Test**: `tests/unit/application/services/test_admin_agent.py` → `test_agent.py` (if exists)
- [ ] **Update**: All imports (~12 files)
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(naming): rename admin_agent to agent (Spec 052)`

### 3-2. IngestionUseCase → Ingestion
- [ ] **Rename Class**: In `app/application/services/ingestion.py`: `IngestionUseCase` → `Ingestion`
- [ ] **Rename Test**: `tests/unit/test_ingestion_use_case.py` → `tests/unit/application/services/test_ingestion.py`
- [ ] **Update**: All class references (~25 files)
- [ ] **Update**: Dependency injection
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(naming): rename IngestionUseCase to Ingestion (Spec 052)`

### 3-3. Core File Simplification
- [ ] **Move**: `app/core/utils/file_processor.py` → `app/core/file_processor.py`
- [ ] **Rename**: `app/core/logging_config.py` → `app/core/logger.py`
- [ ] **Update**: All imports (~15 files)
- [ ] **Cleanup**: Remove `app/core/utils/` directory
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(core): simplify core structure and naming (Spec 052)`

---

## Task 4: State Object Refinement (P3 - Low)

### 4-1. Rename State Files
- [ ] **Rename**: `app/domain/ingestion/state.py` → `app/domain/ingestion/graph_state.py`
- [ ] **Rename**: `app/domain/rag/state.py` → `app/domain/rag/graph_state.py`
- [ ] **Update**: All imports (~10 files)
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `refactor(naming): rename state files to graph_state for clarity (Spec 052)`

---

## Task 5: Duplicate File Cleanup (P3 - Low)

### 5-1. Find and Remove Duplicates
- [ ] **Investigate**: `find app/interfaces/api -name "*.py" | sort`
- [ ] **Verify**: Check if `app/interfaces/api/endpoints/jobs.py` duplicates `v1/endpoints/jobs.py`
- [ ] **Remove**: Delete duplicate if confirmed
- [ ] **Test**: `uv run pytest`
- [ ] **Commit**: `chore(cleanup): remove duplicate endpoint files (Spec 052)`

---

## Task N: Final Verification & PR

- [ ] **Lint Check**: `uv run ruff check .` (0 errors)
- [ ] **Format Check**: `uv run ruff format --check .`
- [ ] **Full Test Suite**: `uv run pytest` (194+ passing)
- [ ] **Import Verification**: Test key imports manually
- [ ] **Documentation**: Write walkthrough.md
- [ ] **Documentation**: Write pr_description.md
- [ ] **Commit**: `docs(spec-052): archive walkthrough and pr description`
- [ ] **Create PR**: Submit for review
