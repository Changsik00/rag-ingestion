# Implementation Plan: Spec-026 (Graph-Enhanced RAG)

## 📋 Branch Strategy
- `feature/spec-026-hybrid-rag`

## 🛑 User Review Required
- **Architecture Change**: Playground에 있던 비즈니스 로직을 `RAGService` (Domain Service)로 이관합니다.
- **Dependency**: Neo4j Fulltext Index 생성을 위해 DB 초기화 또는 인덱스 생성 스크립트 실행이 필요할 수 있습니다.
- **Documentation**: kNN vs MMR 비교 문서는 기술 부채를 줄이기 위해 필수적으로 작성해야 합니다.

## 🎯 Core Strategy
1.  **Graph Context Injection**:
    *   **Entity Extraction**: 질문에서 엔티티 추출.
    *   **Neighbor Search**: `(Entity)-[REL]->(Neighbor)` 관계 조회.
    *   **Fact Conversion**: Triple을 자연어 Fact로 변환하여 주입.
2.  **Maximize Asset Utilization**:
    *   **Vector**: Chroma MMR (Diversity).
    *   **Keyword**: Neo4j Fulltext (Exact Match).
    *   **Graph**: Neo4j Traversal (Relational Context).
3.  **Clean Architecture (RAGService)**:
    *   복잡해진 RAG 파이프라인(Orchestration)을 전담하는 도메인 서비스 도입.

## 📂 Proposed Changes

### [Domain Layer] Service Orchestration

#### [NEW] `app/domain/services/rag_service.py`
- `retrieve_and_generate(query, history)`:
    - 1. Query Rewrite
    - 2. Parallel Search (Vector MMR + Neo4j Keyword + Graph Traversal)
    - 3. Deduplication & Merge
    - 4. Context Formatting (Standardized)
    - 5. LLM QA Generation

### [Infrastructure Layer] Storage Upgrade

#### [MODIFY] `app/infrastructure/storage/neo4j_graph_repository.py`
- `get_subgraph(entities: list[str])`: 엔티티 기준 1-depth 이웃 조회.

#### [MODIFY] `app/infrastructure/storage/neo4j_document_repository.py`
- `create_fulltext_index()`: `Chunk(content)`에 대한 인덱스 생성.
- `search(query)`: Cypher `CALL db.index.fulltext.queryNodes` 활용.

#### [MODIFY] `app/infrastructure/storage/chroma.py`
- `search_mmr(query, limit, diversity)`: LangChain/Python 알고리즘을 차용한 MMR 구현.

### [UI Layer] Playground

#### [MODIFY] `app/admin/pages/4_RAG_Playground.py`
- 직접 `repo.search` 하던 코드를 `RAGService` 호출로 변경 (Refactoring).
- Debug Info: Graph Fact와 Vector Chunk를 구분하여 표시.

## 🧪 Verification Plan

### Automated Tests
#### 1. Integration Tests
```bash
# Graph Retrieval Logic 검증
uv run pytest tests/integration/test_neo4j_graph_retrieval.py

# Hybrid Merge & MMR 검증
uv run pytest tests/integration/test_hybrid_rag_flow.py
```

### Manual Verification
- **Scenario A: Graph Fact Injection**
    - Input: "일론 머스크의 회사는?" (텍스트에 '테슬라' 없다고 가정)
    - Check: Graph Fact `(Elon)-[FOUNDED]->(Tesla)`가 프롬프트에 주입되어 정답을 맞추는지 확인.
- **Scenario B: Citation Check**
    - Input: 위키 데이터 질문
    - Check: 답변에 `[Source: https://ko.wikipedia...]` 포함 여부 확인.
