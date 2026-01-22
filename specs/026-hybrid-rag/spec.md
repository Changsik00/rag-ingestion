# Spec-026: Hybrid RAG & Metadata Strategy (Graph-Enhanced)

## 📋 배경 및 문제 정의 (Background & Problem)
Spec-025 검증 과정에서 시스템의 치명적인 **전략적 결함(Strategic Flaws)**이 드러났습니다. 이를 해결하지 않으면 RAG의 신뢰성을 담보할 수 없습니다.

1.  **Fake Hybrid RAG (무늬만 하이브리드)**:
    *   현재 `CompositeStorage`는 Neo4j(Graph)와 Chroma(Vector)에 모두 저장하지만, 검색 시에는 **오직 Vector DB만 사용**합니다 (Graph Write-Only).
    *   이로 인해 우리가 구축한 온톨로지(Ontology) 자산이 검색에 전혀 활용되지 못하고 있습니다.

2.  **Metadata Underutilization (데이터 편식)**:
    *   LLM에게 `Content`만 제공하고 메타데이터(URL, Title)를 제공하지 않아, AI가 가짜 출처를 생성하는 **환각(Hallucination)**이 발생했습니다.

3.  **Lack of Diversity (편협한 검색)**:
    *   기존 kNN 방식은 유사한 문장(중복)만 상위에 노출하여 정보의 다양성이 떨어집니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **Hybrid & Graph Retrieval**:
    *   **Keyword Search**: Neo4j Fulltext Index를 활용하여 키워드 매칭 문서를 검색.
    *   **Graph Traversal**: 질문의 핵심 엔티티(Entity Linking)를 파악하고, 연결된 1-depth 관계(Relationship)를 조회.
    *   **Context Injection**: `Vector Context` + `Graph Fact`를 결합하여 LLM에 제공.

2.  **Citation Enforcement**:
    *   **Standardized Format**: `[Source ID] Title: ... Content: ...` 형태로 문맥 포맷 표준화.
    *   **Prompt Rule**: 출력 시 반드시 제공된 출처를 인용하도록 강제.

3.  **Vector Diversity**:
    *   **MMR Search**: Chroma 검색 시 MMR(Maximal Marginal Relevance) 알고리즘을 적용하여 정보 다양성 확보.

### Non-Functional Requirements
1.  **Latency Management**: 두 DB를 조회하므로 성능 저하가 우려됨. 병렬(Async) 처리를 원칙으로 함.
2.  **Compatibility**: 기존 RAG Playground 기능과 호환되어야 함.

## ✅ Definition of Done
1.  **Hybrid Search**: `repo.search()` 호출 시 Neo4j와 Chroma 양쪽에서 로그가 출력되어야 함.
2.  **Graph Injection**: "일론 머스크" 검색 시, 텍스트에 없는 Graph Fact(예: 창립 회사)가 프롬프트에 포함되어야 함.
3.  **Accurate Citation**: Playground 답변에 실제 Wiki URL이 인용(`[Source]`)되어야 함.
4.  **MMR Verification**: "MMR vs kNN" 비교 문서를 작성하여 다양성 효과를 증명.
