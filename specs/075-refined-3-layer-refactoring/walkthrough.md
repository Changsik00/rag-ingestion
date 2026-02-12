# RAG 3-Layer Refactoring Walkthrough

## Overview
Refactored the RAG system into a clean 3-Layer Architecture (Brain, Retrieval, Orchestration) as per Spec 075. This improves separation of concerns, testability, and scalability.

## Changes

### 1. New Architecture Components

#### Brain Layer (`app/domain/rag/brain/`)
- **`BrainService`**: Handles Intent Classification and Query Rewriting.
- **`Reranker`**: Handles document reranking (moved from Retrieval).
- **`AnswerGenerator`**: Handles final answer generation and citation parsing.

#### Retrieval Layer (`app/infrastructure/rag/retrieval/`)
- **`RetrievalService`**: Dedicated to Hybrid Search (Vector + Keyword + Graph). No longer handles reranking or storage updates.
- **`clean_context_noise`**: Extracted text cleaning logic to `app/domain/rag/text_cleaner.py`.

#### Orchestration Layer (`app/application/rag/orchestration/`)
- **`RAGOrchestrator`**: Central coordinator that wires Brain and Retrieval services.
  - Implements `classify`, `route_filters`, `search`, `rerank`, `generate` methods.
  - Manages the state transitions and fallback logic.

### 2. Graph Builder Refactoring (`app/infrastructure/ai/rag_graph.py`)
- Replaced the legacy `RAGGraphBuilder` (which used `RAGNodes`) with a new implementation that uses `RAGOrchestrator`.
- The new builder maps graph nodes (adapters) directly to orchestrator methods, ensuring granular control and visibility.

### 3. Dependency Injection (`app/interfaces/api/dependencies.py`)
- Updated `get_rag_graph_builder` to use `RAGOrchestrator`.
- Added providers for `BrainService`, `RetrievalService`, `Reranker`, `AnswerGenerator`, and `RAGOrchestrator` using `lru_cache`.
- Removed legacy `get_rag_nodes`.

### 4. Cleanup
- **Deleted**: `app/infrastructure/ai/rag_nodes.py` (Legacy monolithic class).
- **Deleted**: `tests/unit/infrastructure/rag/test_rag_nodes.py` and related legacy tests.
- **Updated**: `app/application/services/integrity.py` and `app/interfaces/mcp/server.py` to remove `RAGNodes` usage.

## Verification

### Automated Tests
- **Unit Tests**:
  - `BrainService`, `Reranker`, `AnswerGenerator`, `RetrievalService`, `RAGOrchestrator` all have passing unit tests.
- **Integration Test**:
  - `tests/integration/rag/test_rag_graph_wiring.py`: Verifies the end-to-end wiring of the RAG graph using the new components.
  - `tests/integration/scenarios/test_rag_mocked_flow.py`: Verifies the RAG service contract with mocked graph.

All tests passed successfully (ignoring unrelated collection warnings).

### Manual Verification
- Verified that `dependencies.py` correctly wires the new graph into the `RAG` service used by API endpoints.

## Conclusion
The RAG system is now successfully refactored to the 3-Layer Architecture. The codebase is cleaner, more modular, and aligned with the architectural vision.
