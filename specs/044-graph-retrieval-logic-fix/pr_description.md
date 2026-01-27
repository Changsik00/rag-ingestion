# feat(spec-044): graph retrieval logic fix

## 📋 Summary
기존 RAG는 질문 전체를 Vector Search로 검색하여, "A와 B의 관계"와 같은 질문에서 구체적인 관계를 찾지 못하는 문제가 있었습니다.
이를 해결하기 위해 `IntentClassifier` 단계에서 Entity를 명시적으로 추출하고, Neo4j의 `shortestPath` 알고리즘을 사용하여 Entity 간의 관계(Graph Context)를 직접 조회하도록 개선했습니다.

## 🎯 Key Review Points
1. **Intent Classifier**: Prompt가 변경되어 `entities` 필드를 추가로 반환합니다. 기존 Intent 분류 성능에 영향이 없는지 확인 부탁드립니다.
2. **Neo4j Repository**: `find_shortest_path` 메서드가 추가되었습니다. 2개 이상의 Entity가 주어졌을 때 최단 경로를 탐색합니다.
3. **RAG Flow**: `RAGNodes.retrieve_hybrid`에서 Entity 유무에 따라 `_search_graph`의 동작이 분기됩니다.

## 🧪 Verification
### Automated Tests
```bash
# Entity Extraction Unit Test
uv run pytest tests/unit/test_intent_classifier.py

# Graph Retrieval Logic Test (Mocked)
uv run pytest tests/unit/test_rag_nodes_spec044.py

# Neo4j Integration Test
uv run pytest tests/integration/test_neo4j_graph_retrieval.py
```

## 📦 Files Changed

### 🆕 New Files
- `tests/unit/test_rag_nodes_spec044.py`: RAG Node의 로직 분기 검증 테스트
- `docs/design_guides/010-graph-retrieval-logic.md`: 해결 전략 기술 문서
- `specs/044-graph-retrieval-logic-fix/`: Spec, Plan, Task 문서

### 🛠 Modified Files
- `app/domain/schemas/intent.py`: `entities` 필드 추가
- `app/domain/services/intent_classifier.py`: Prompt 수정 (Entity 추출 지시)
- `app/infrastructure/rag/nodes.py`: `retrieve_hybrid` 및 `_search_graph` 수정
- `app/infrastructure/store/neo4j_graph_repository.py`: `find_shortest_path` 구현
- `tests/integration/test_neo4j_graph_retrieval.py`: `find_shortest_path` 테스트 추가

## ✅ Definition of Done
- [x] `IntentClassifier`가 질문에 포함된 Entity를 정확히 추출함을 단위 테스트로 검증한다.
- [x] 추출된 Entity를 이용해 Neo4j에서 관계 데이터를 가져오는 Integration Test가 통과해야 한다.
- [x] "일론 머스크와 트위터의 관계는?" 질문 시 RAG가 Graph Context를 활용하여 답변하는지 검증한다 (Manual/Playground).
