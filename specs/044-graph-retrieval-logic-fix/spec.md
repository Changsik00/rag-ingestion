# Spec-044: Graph Retrieval Logic Fix (Entity-based Search)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 RAG 시스템은 질문 전체를 임베딩하여 Graph DB를 검색(Vector Search)하고 있으나, "A와 B의 관계는?"과 같은 관계형 질문에서 Graph DB의 장점을 살리지 못하고 있다. 질문의 임베딩 벡터와 개별 Entity 노드 간의 유사도가 낮아 검색이 실패하기 때문이다.
이 문제를 해결하기 위해, 질문에서 Entity를 명시적으로 추출하고, 이를 기반으로 Graph DB를 직접 조회(Traversal)하는 로직이 필요하다.

**관련 문서**: [Design Guide 010: Graph Retrieval Logic Fix](../../docs/design_guides/010-graph-retrieval-logic.md)

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **Entity Extraction**: 사용자의 질문에서 Graph 검색에 사용할 Entity 목록(예: "일론 머스크", "트위터")을 추출해야 한다.
2.  **Intent Classification Update**: 기존 `IntentClassifier`가 Intent뿐만 아니라 `Entities` 리스트도 반환하도록 개선한다.
3.  **Graph Traversal**: 추출된 Entity를 기반으로 Neo4j에서 관련 노드 및 관계를 탐색하는 Cypher Query를 실행해야 한다.
4.  **Context Injection**: Graph DB에서 탐색된 관계 정보를 자연어 또는 구조화된 텍스트로 변환하여 LLM Context에 포함시켜야 한다.

### Non-Functional Requirements
1.  **Response Time**: Graph 탐색 쿼리가 전체 응답 시간을 과도하게 지연시키지 않아야 한다 (Timeout 설정 필요).

## ✅ Definition of Done
1.  `IntentClassifier`가 질문에 포함된 Entity를 정확히 추출함을 단위 테스트로 검증한다.
2.  추출된 Entity를 이용해 Neo4j에서 관계 데이터를 가져오는 Integration Test가 통과해야 한다.
3.  "일론 머스크와 트위터의 관계는?" 질문 시 RAG가 Graph Context를 활용하여 답변하는지 검증한다 (Manual/Playground).
