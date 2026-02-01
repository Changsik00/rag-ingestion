# Refactor: Clean Architecture Layer Refinement (Spec 052)

## 🎯 Objective
Refine the architectural boundaries and naming conventions to strictly adhere to Clean Architecture principles. This PR addresses remaining technical debt identified in Spec 051, focusing on consistent layer placement and clear naming.

## 🛠 Key Changes

### 1. Architecture Layer Corrections
- **Moved Interfaces**: `LLMInterface` and `ScraperInterface` moved from `domain` to `application/interfaces`. (Interfaces defined by the application needs, implemented by infrastructure).
- **Moved Services**: `Feedback` service moved from `domain` to `application/services`.
- **Value Objects**: `DocumentMetadata` moved to `domain/value_objects`.

### 2. Naming & Structure Standardization
- **Agent Renaming**: `admin_agent.py` → `agent.py`. The agent is a general conversational agent, not limited to "admin" functions.
- **Service Class Renaming**: `IngestionUseCase` → `Ingestion`. Standardized with other services like `Integrity` and `Feedback`.
- **Core Refactoring**: Flattened `core/utils/` into `core/` and renamed `logging_config.py` to `logger.py`.
- **State Clarification**: Renamed `state.py` to `graph_state.py` in both `ingestion` and `rag` domains to avoid ambiguity.

### 3. Code Cleanup
- Removed legacy duplicate API endpoint file: `app/interfaces/api/endpoints/jobs.py`.
- Updated all relevant imports.

## ✅ Verification
- **Tests**: All 194 tests passed.
- **Linting**: `ruff` check and format passed.

## 🔗 Related Specs
- **Spec 052**: Clean Architecture Layer Refinement
- **Spec 051**: Architecture Refinement (Consistency & Cleanliness)
