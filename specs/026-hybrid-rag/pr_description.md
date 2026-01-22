feat(spec-026): hybrid rag strategy implementation

## 📋 Summary
기존의 단순 Vector 검색(ChromaDB) 방식을 **Graph-Enhanced Hybrid Search** 전략으로 업그레이드했습니다.
이제 `RAGService`가 중심이 되어 **Vector(MMR)**, **Keyword(Neo4j)**, **Graph Traversal(Neo4j)** 세 가지 검색 방식을 병렬로 수행하고, 결과를 통합하여 LLM에게 풍부하고 정확한 구조적 지식을 제공합니다.

- **Before**: ChromaDB kNN 검색만 수행 -> 문맥 부족 및 환각 발생 가능성 높음.
- **After**: Vector(Semantic) + Keyword(Exact) + Graph(Fact) 통합 검색 -> `RAGService`가 결과 병합 및 Citation 포맷팅 수행.

## 🎯 Key Review Points
1. **RAGService 도입 (`app/domain/services/rag_service.py`)**:
    - 검색 로직을 도메인 서비스로 격리하고, `asyncio.gather`를 통해 병렬 검색을 수행합니다.
    - 검색 결과(`Chunk`)와 그래프 사실(`Triples`)을 통합된 `RAGResult` DTO로 반환합니다.

2. **Vector Diversity (MMR) (`app/infrastructure/storage/chroma.py`)**:
    - 중복된 내용을 배제하고 다양성을 확보하기 위해 kNN 대신 **MMR (Maximal Marginal Relevance)** 알고리즘을 구현했습니다.
    - `numpy`를 사용하여 코사인 유사도를 직접 계산합니다.

3. **Neo4j Fulltext & Graph (`app/infrastructure/storage/neo4j_*.py`)**:
    - `Neo4jDocumentRepository`: Fulltext Index를 활용한 키워드 검색 추가.
    - `Neo4jGraphRepository`: 1-depth Subgraph 조회를 위한 `get_subgraph` 구현.

4. **Playground Debugging (`app/admin/pages/4_RAG_Playground.py`)**:
    - 사용자가 검색 과정(Rewritten Query, Graph Facts, MMR Results)을 투명하게 볼 수 있도록 Debug View를 개선했습니다.

## 🧪 Verification
### Automated Tests
```bash
# 1. Real DB 연결 테스트 (Hybrid Search 파이프라인 검증)
uv run pytest tests/integration/test_hybrid_retrieval.py

# 2. RAGService 오케스트레이션 로직 테스트 (Mock)
uv run pytest tests/integration/test_rag_service.py

# 3. MMR 알고리즘 동작 검증
uv run pytest tests/integration/test_chroma_repository.py
```

### Manual Verification
1. **Playground 접속**: `4_RAG_Playground` 페이지 이동.
2. **질의 수행**: 예: "일론 머스크" 검색.
3. **Debug 확인**:
    - 🛠️ Debug: Prompt & Rewriting -> 쿼리 재구성 확인.
    - 🕸️ Graph Facts -> `(Elon Musk)-[FOUNDED]->(Tesla)` 등의 트리플 확인.
    - 📚 Retrieved Documents -> Vector/Keyword 탭 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/rag_service.py`: Hybrid RAG 오케스트레이션 로직 및 `RAGResult` DTO.
- `tests/integration/test_hybrid_retrieval.py`: 실제 DB 연동 통합 테스트.
- `tests/integration/test_rag_service.py`: 서비스 로직 단위/통합 테스트.
- `docs/design_guides/004-graph-rag-strategy.md`: Graph-Enhanced RAG 아키텍처 및 전략 문서.

### 🛠 Modified Files
- `app/infrastructure/storage/chroma.py`: `search_mmr` 메서드 추가 및 NumPy 기반 구현.
- `app/infrastructure/storage/neo4j_document_repository.py`: Fulltext Index 생성 및 검색 로직 추가.
- `app/infrastructure/storage/neo4j_graph_repository.py`: `get_subgraph` 구현 (List[str] 입력 지원).
- `app/admin/pages/4_RAG_Playground.py`: `RAGService` 연동 및 UI 개선.

## ✅ Definition of Done
- [x] Spec 026의 Hybrid Search (Vector+Keyword+Graph) 구현 완료
- [x] RAGService를 통한 검색 오케스트레이션 적용
- [x] Playground UI에 Graph Fact 및 상세 디버그 정보 표시
- [x] 모든 통합 테스트(Hybrid, MMR, Service) 통과
- [x] Linting (`ruff check`) 통과
