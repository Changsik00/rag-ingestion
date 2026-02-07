# Walkthrough: Spec-067 Advanced Reranking

## 🚀 개요
본 작업에서는 RAG 파이프라인의 정밀도를 높이기 위해 기존의 Pointwise 리랭킹 방식을 개선하여 **Listwise Reranking** 및 **Context Window Expansion (Sliding Window)** 기능을 구현했습니다.

## ✨ 변경 사항

### 1. Repository Layer
- **[DocumentRepository](file:///Users/ck/Project/doit/rag-ingestion/app/domain/interfaces/document_repository.py)**: `get_adjacent_chunks` 추상 메서드 추가.
- **[Neo4jDocumentRepository](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/repositories/neo4j_document_repository.py)**: Cypher 쿼리를 이용해 인접 청크를 효율적으로 조회하는 로직 구현.

### 2. Domain & Prompt
- **[Listwise Prompt](file:///Users/ck/Project/doit/rag-ingestion/app/domain/services/prompts/listwise_reranker.py)**: 여러 청크를 동시에 비교 분석하여 순위를 매기는 프롬프트 추가.
- **[RAG State](file:///Users/ck/Project/doit/rag-ingestion/app/domain/value_objects/rag_state.py)**: `rerank_strategy` 필드를 추가하여 유연한 전략 선택 지원.

### 3. Body Layer (RAG Nodes)
- **[RAGNodes](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/ai/rag_nodes.py)**:
    - `_expand_context_window`: 청크 평가 시 전후 맥락을 결합하여 정보 파편화 문제 해결.
    - `_rerank_listwise`: LLM에게 청크 리스트를 전달하여 상대적 중요도 기반 재정렬 수행.
    - `rerank_results`: 전략(Pointwise/Listwise)에 따른 분기 로직 구현.

## 🧪 검증 결과

### 코드 품질
- `ruff check` 및 `ruff format`을 통해 코드 컨벤션 준수 확인.

### 로직 동작 확인
- `rerank_strategy="pointwise"` (기본값) 환경에서 기존 로직이 안정적으로 동작함을 확인.
- `listwise` 모드 호출 시 `_expand_context_window`를 통해 인접 청크가 정상적으로 병합되고 프롬프트에 포함됨을 확인.

## 📸 실행 로그 (예시)
```text
🎯 [Rerank/Listwise] Analyzed 10 chunks. 6 passed, 4 dropped.
🎯 [Rerank/Pointwise] Analyzed 15 chunks. 8 passed, 7 dropped.
```
