# Spec 024: Advanced Admin Dashboard Walkthrough

## 1. Overview
This walkthrough demonstrates the new **Advanced Admin Dashboard** implemented in Spec 024. The dashboard provides full observability into the RAG Pipeline, including Job Monitoring, Graph Visualization, HITL Control, and a transparent RAG Playground.

## 2. Features Walkthrough

### 2.1 Job Queue
Monitors the status of Ingestion Jobs.
- **Path**: `app/admin/pages/0_Job_Queue.py`
- **Function**: Lists jobs from Neo4j (`IngestionJob` nodes), showing status (`PENDING`, `COMPLETED`, `FAILED`) and source URL.

### 2.2 Graph Explorer
Visualizes the Knowledge Graph.
- **Path**: `app/admin/pages/1_Graph_Explorer.py`
- **Function**: Uses `search_graph` to fetch nodes/edges and renders them using `streamlit-agraph`.
- **Features**: Presets (e.g., "Show All People") vs Custom Cypher queries.

### 2.3 RAG Playground (Enhanced)
A "Glass Box" interface for testing retrieval quality.
- **Path**: `app/admin/pages/4_RAG_Playground.py`
- **Real Generation**: Connected to Gemini via `LangChainLLMAdapter`.
- **Hybrid Mode**: Explicit prompt rules to use Context first, then General Knowledge fallback.
- **Debug View**: `🛠️ Debug: Prompt & Logic` expander shows the exact prompt sent to the LLM, enabling "Reasoning Trace" inspection.

### 2.4 HITL Control & Trace
Manages Human-in-the-Loop workflows.
- **Path**: `app/admin/pages/2_HITL_Control.py`, `3_Trace_Viewer.py`
- **Function**: Lists interrupted threads from SQLite checkpointer. Allows Resume/Cancel operations.

## 3. Deployment & Architecture
- **Docker**: New `rag-admin` container running Streamlit on port 8501.
- **Networking**: Uses internal container names (`rag-neo4j`, `rag-backend`) for reliable DNS resolution.
- **Security**: Database credentials and API Keys injected via environment variables.

## 4. Spec 026: Graph-Enhanced RAG (Hybrid Search)

### 4.1 Overview
Overcame the "Vector-Only" limitation by integrating Neo4j for Keyword and Graph retrieval.
- **Hybrid Search**: `Vector(MMR)` + `Keyword(Neo4j Fulltext)` + `Graph(Neo4j Subgraph)`.
- **RAGService**: Unified orchestration service.
- **MMR**: Diversity check implemented in `ChromaStorage` (NumPy based).

### 4.2 Verification Results
**Automated Tests**:
- `tests/integration/test_hybrid_retrieval.py`: Passed (Real DB connection).
- `tests/integration/test_rag_service.py`: Passed (Orchestration logic).

**Manual Playground Test**:
1. Searched "Test Query".
2. Observed "Graph Facts" in Debug View.
3. Observed "Vector Search (MMR)" and "Keyword Search" sections.
4. Confirmed `RAGService` orchestration works end-to-end.

## 5. Next Steps
- **Spec ???**: Visualization of MCP Server tools.

