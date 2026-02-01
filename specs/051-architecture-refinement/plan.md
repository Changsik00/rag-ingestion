# Implementation Plan: Spec-051 (Hierarchical AI Structure)

## 📋 Branch Strategy
- `feature/051-architecture-refinement`

## 🛑 User Review Required
> [!WARNING]
> - [ ] **Folder Deletions**: This plan involves explicitly deleting `app/infrastructure/llm` and `app/infrastructure/brain`. All contents will be moved to `app/infrastructure/ai/`.
> - [ ] **Massive Renaming**: `storage` -> `repositories`, `schemas` -> `dto`.

## 🎯 Core Strategy

### Architecture Context
Consolidate fragmented AI logic (`llm`, `brain`, `rag`) into a unified, hierarchical `ai` directory to improve discoverability and cohesion.

| Component | Destination | Reasoning |
|:---|:---|:---|
| **LLM Adapter** | `ai/extractors/langchain_extractor.py` | It extracts metadata using LLM. |
| **Brain Adapter** | `ai/orchestrators/ingestion_orchestrator.py` | It orchestrates the ingestion graph. |
| **Brain Graph** | `ai/graphs/ingestion_graph.py` | Definition of the ingestion graph. |
| **Brain Nodes** | `ai/nodes/ingestion_nodes.py` | Nodes used in ingestion. |
| **Rag Graph** | `ai/graphs/rag_graph.py` | Definition of RAG graph (Future consolidation). |
| **FileProcessor** | `core/utils/file_processor.py` | Generic stateless utility. |

## 📂 Proposed Changes

### P1: High Priority (Core Domain & Semantic Naming)

#### [MODIFY] `app/application/services/integrity_service.py` -> `integrity.py`
#### [MODIFY] `app/domain/services/feedback_service.py` -> `feedback.py`

#### [NEW] `app/domain/value_objects/chunk.py` (Pydantic VO)
#### [NEW] `app/domain/models/document_metadata.py` (Pydantic VO)
#### [DELETE] `app/domain/entities/chunk.py`

#### [NEW] `app/domain/interfaces/chunker.py` (Protocol)

### P2: Medium Priority (Structural Cleanup & Consolidation)

#### [NEW DIR] `app/infrastructure/ai/{extractors,orchestrators,nodes,graphs}`

#### [MOVE & RENAME]
- `infrastructure/llm/langchain_adapter.py` -> `ai/extractors/langchain_extractor.py`
- `infrastructure/brain/adapter.py` -> `ai/orchestrators/ingestion_orchestrator.py`
- `infrastructure/brain/nodes.py` -> `ai/nodes/ingestion_nodes.py`
- `infrastructure/brain/graph.py` -> `ai/graphs/ingestion_graph.py`
- `infrastructure/brain/logic.py` -> `ai/logic/ingestion_logic.py` (if Logic exists)

#### [DELETE DIR] `app/infrastructure/llm`, `app/infrastructure/brain`

#### [MOVE] `app/domain/services/file_processor.py` -> `app/core/utils/file_processor.py`

#### [RENAME] `app/infrastructure/storage/` -> `app/infrastructure/repositories/`
- Rename files to end with `_repository.py`.

### P3: Low Priority (Standardization)

#### [RENAME] States
- `IngestionState` -> `IngestionGraphState`.
- `RAGState` -> `RAGGraphState`.

#### [RENAME] DTO
- `schemas` -> `dto`.

#### [RENAME] Agent
- `AdminAgent` -> `ConversationalRAGAgent`.

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (VOs)
uv run pytest tests/unit/domain/value_objects/test_chunk.py

# Integration Tests (Critical path for moved files)
uv run pytest tests/integration/test_ingestion_flow.py
```

### Manual Verification
1.  **Directory Check**: Ensure `llm` and `brain` folders are GONE.
2.  **Import Check**: Search for `app.infrastructure.brain` imports and ensure 0 results.
