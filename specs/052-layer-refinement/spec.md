# Spec 052: Clean Architecture Layer Refinement

## 🎯 Objective
Apply strict Clean Architecture layer boundaries by moving misplaced components to their correct layers, improving naming consistency, and eliminating redundant file structures from the Spec 051 refactoring.

## 📋 Background

After the comprehensive Spec 051 refactoring, several architectural inconsistencies remain:

1. **Layer Violations**: Some interfaces are in `domain/` when they should be in `application/`
2. **Naming Inconsistencies**: File names don't always match their content or peer naming patterns
3. **Redundant Structures**: Some files use unnecessary nesting (e.g., `core/utils/`)
4. **Duplicate Files**: Legacy files coexist with their refactored versions

## 🔍 Issues to Address

### 1. Layer Boundary Violations

**Domain → Application Migration:**
- `app/domain/interfaces/llm.py` → `app/application/interfaces/llm.py`
  - Reason: LLM is an infrastructure concern, not a core domain concept
- `app/domain/interfaces/scraper.py` → `app/application/interfaces/scraper.py`
  - Reason: Web scraping is an external service, not domain logic
- `app/domain/services/feedback.py` → `app/application/services/feedback.py`
  - Reason: Orchestrates LangGraph workflow, which is application-level coordination

### 2. Value Object Reorganization

- `app/domain/models/document_metadata.py` → `app/domain/value_objects/document_metadata.py`
  - Reason: `DocumentMetadata` is immutable and has no identity (classic VO)

### 3. Naming Consistency

**File Renaming:**
- `app/application/services/admin_agent.py` → `app/application/services/agent.py`
  - Contains `ConversationalRAGAgent`, not "admin" specific
- `app/application/services/ingestion.py` (IngestionUseCase) → Keep filename but rename class to `Ingestion`
  - Consistency with `Integrity`, `Feedback`
- `app/core/utils/file_processor.py` → `app/core/file_processor.py`
  - `core/` already implies utility nature
- `app/core/logging_config.py` → `app/core/logger.py`
  - Simpler, more conventional

### 4. State Object Clarification

**Current State:**
- `app/domain/ingestion/state.py` contains `IngestionGraphState`
- `app/domain/rag/state.py` contains `RAGGraphState`

**Decision Needed:**
These are TypedDict-based LangGraph states with technical constraints. Options:
1. Keep in domain with renamed files: `graph_state.py`
2. Move to `infrastructure/ai/graphs/` (closer to usage)
3. Create `application/graph_states/` (middle ground)

**Recommendation:** Keep in domain but rename files for clarity.

### 5. Duplicate File Cleanup

- Verify and remove: `app/interfaces/api/endpoints/jobs.py` if it duplicates `v1/endpoints/jobs.py`

## ✅ Success Criteria

1. All interfaces correctly placed in appropriate layers
2. File names consistently reflect their contents
3. No unnecessary directory nesting
4. All tests pass after migrations
5. Import paths updated across entire codebase

## 📦 Deliverables

1. Refactored file structure following Clean Architecture strictly
2. Updated import statements (200+ files estimated)
3. Passing test suite
4. PR documentation with clear migration guide

## 🔗 Related Work

- Spec 051: Architecture Refinement (hierarchical AI structure)
- Design Guide 012: Architecture Refinement Principles
