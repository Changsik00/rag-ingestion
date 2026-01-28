# Implementation Plan: Spec-044

## 📋 Branch Strategy
- `feature/spec-044-graph-retrieval-fix`

## 🛑 User Review Required
- [ ] IntentClassifier의 Prompt 변경이 기존 Intent 분류 정확도에 영향을 주는지 확인 필요.

## 🎯 Core Strategy
- **IntentClassifier 확장**: 별도의 Entity Extractor를 만드는 대신, 기존 분류 단계에서 Entity 추출을 함께 수행하여 Latency 증가를 최소화함.
- **Shortest Path Strategy**: 두 개 이상의 Entity가 추출된 경우, 두 Entity 사이의 최단 경로(`shortestPath`)를 우선 탐색하여 관계를 파악함.

## 📂 Proposed Changes

### [Core / Brain]
#### [MODIFY] `app/infrastructure/brain/nodes.py`
- `IntentClassifier` 프롬프트 수정 (Entity 추출 지시 추가)
- Pydantic Model (`IntentResult`)에 `entities: List[str]` 필드 추가

#### [MODIFY] `app/domain/rag/service.py`
- `retrieve` 로직 흐름 수정: Intent 결과에 Entities가 있으면 `neo4j_repo.find_subgraph` 호출 추가
- 검색된 Graph Context를 기존 Vector Context와 병합

### [Infrastructure / Store]
#### [MODIFY] `app/infrastructure/store/neo4j_document_repository.py`
- `find_subgraph_by_entities(entities)` 메서드 구현
- Cypher Query: Entity Name 매칭 및 관계 조회

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (Intent Classifier)
uv run pytest tests/unit/test_intent_classifier.py

# Integration Tests (Neo4j Retrieval)
uv run pytest tests/integration/test_graph_retrieval.py
```

### Manual Verification
1. Admin Dashboard > RAG Playground 접속
2. "일론 머스크와 트위터의 관계는?" 입력 (Interactive Mode Off)
3. "Graph Search" 로그에 추출된 Entity와 Cypher 실행 결과(관계 데이터)가 찍히는지 확인.
