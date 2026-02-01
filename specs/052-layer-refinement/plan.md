# Implementation Plan: Spec 052 - Clean Architecture Layer Refinement

## 🎯 Goal
Fix layer boundary violations and naming inconsistencies left over from Spec 051, ensuring strict adherence to Clean Architecture principles.

## 🗺️ Execution Strategy

### Phase 1: Layer Boundary Corrections (High Priority)
Move misplaced interfaces and services to their correct architectural layers.

### Phase 2: Naming Standardization (Medium Priority)
Rename files and classes for consistency and clarity.

### Phase 3: Structure Cleanup (Low Priority)
Remove redundant nesting and duplicate files.

---

## 📋 Task Breakdown

### Task 1: Interface Layer Migration

#### 1-1. LLM Interface Migration
**Files:**
- `app/domain/interfaces/llm.py` → `app/application/interfaces/llm.py`

**Impact Analysis:**
```bash
grep -r "from app.domain.interfaces.llm" app/ tests/
```

**Steps:**
1. Create `app/application/interfaces/` directory if needed
2. Move `llm.py` to new location
3. Update all imports across codebase
4. Run tests to verify

**Estimated Imports to Update:** ~15 files

#### 1-2. Scraper Interface Migration
**Files:**
- `app/domain/interfaces/scraper.py` → `app/application/interfaces/scraper.py`

**Impact Analysis:**
```bash
grep -r "from app.domain.interfaces.scraper" app/ tests/
```

**Steps:**
1. Move `scraper.py` to `application/interfaces/`
2. Update all imports
3. Run tests

**Estimated Imports to Update:** ~8 files

#### 1-3. Feedback Service Migration
**Files:**
- `app/domain/services/feedback.py` → `app/application/services/feedback.py`

**Impact Analysis:**
```bash
grep -r "from app.domain.services.feedback" app/ tests/
grep -r "app.domain.services.feedback" app/ tests/
```

**Steps:**
1. Move `feedback.py` to `application/services/`
2. Update all imports and dependency injection
3. Update test file location
4. Run tests

**Estimated Imports to Update:** ~10 files

---

### Task 2: Value Object Reorganization

#### 2-1. DocumentMetadata Migration
**Files:**
- `app/domain/models/document_metadata.py` → `app/domain/value_objects/document_metadata.py`

**Impact Analysis:**
```bash
grep -r "from app.domain.models.document_metadata" app/ tests/
```

**Steps:**
1. Move file to `value_objects/`
2. Update imports
3. Consider removing `models/` directory if empty

**Estimated Imports to Update:** ~20 files

---

### Task 3: File and Class Renaming

#### 3-1. Admin Agent → Agent
**Files:**
- `app/application/services/admin_agent.py` → `app/application/services/agent.py`

**Impact Analysis:**
```bash
grep -r "admin_agent" app/ tests/
```

**Steps:**
1. Rename file
2. Update all imports
3. Update test file name if exists

**Estimated Imports to Update:** ~12 files

#### 3-2. IngestionUseCase → Ingestion
**Files:**
- `app/application/services/ingestion.py` (class rename only)

**Steps:**
1. Rename `IngestionUseCase` class to `Ingestion`
2. Update all references
3. Update dependency injection
4. Update test file name

**Estimated References to Update:** ~25 files

#### 3-3. Core File Simplification
**Files:**
- `app/core/utils/file_processor.py` → `app/core/file_processor.py`
- `app/core/logging_config.py` → `app/core/logger.py`

**Steps:**
1. Move `file_processor.py` up one level
2. Rename `logging_config.py` to `logger.py`
3. Remove `utils/` directory if empty
4. Update all imports

**Estimated Imports to Update:** ~15 files

---

### Task 4: State Object Refinement

#### 4-1. Rename State Files for Clarity
**Files:**
- `app/domain/ingestion/state.py` → `app/domain/ingestion/graph_state.py`
- `app/domain/rag/state.py` → `app/domain/rag/graph_state.py`

**Rationale:** Make it explicit these are LangGraph technical constraints, not domain entities.

**Steps:**
1. Rename files
2. Update imports
3. Run tests

**Estimated Imports to Update:** ~10 files

---

### Task 5: Duplicate File Cleanup

#### 5-1. Find and Remove Duplicates
**Commands:**
```bash
find app/interfaces/api -name "jobs.py"
find app/interfaces/api -name "*.py" -type f
```

**Steps:**
1. Identify duplicate or orphaned endpoint files
2. Verify they're truly unused (check imports, git history)
3. Remove if confirmed duplicate
4. Run tests

---

## 🧪 Testing Strategy

### Per-Task Testing
After each file move/rename:
```bash
uv run pytest tests/unit/
uv run pytest tests/integration/
```

### Final Validation
```bash
# Full test suite
uv run pytest

# Linting
uv run ruff check .

# Import verification
python -c "from app.application.services.agent import ConversationalRAGAgent"
python -c "from app.application.interfaces.llm import SemanticExtractor"
```

---

## 📊 Risk Assessment

**High Risk:**
- Interface migrations (many import changes)
- IngestionUseCase rename (used extensively)

**Medium Risk:**
- File processor path change
- Admin agent rename

**Low Risk:**
- State file renames
- Logger rename
- Duplicate removal

---

## 🚀 Execution Order

1. **Task 1** (Interfaces): Critical for clean architecture compliance
2. **Task 2** (Value Objects): Dependency for Task 1
3. **Task 3.2** (IngestionUseCase): High impact, do early
4. **Task 3** (Other Renames): Lower risk
5. **Task 4** (State): Can be done anytime
6. **Task 5** (Cleanup): Final step

---

## ✅ Definition of Done

- [ ] All files moved to correct architectural layers
- [ ] All imports updated and verified
- [ ] Zero linting errors
- [ ] All tests passing (194+ tests)
- [ ] PR documentation complete
- [ ] Design guide updated if needed
