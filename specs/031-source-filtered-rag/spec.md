# Spec 031: Source-Filtered RAG (Contextual Isolation)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 RAG 서비스는 사용자의 질문에 대해 전체 지식 베이스(Graph + Vector)를 대상으로 검색을 수행합니다. 이로 인해 다음과 같은 문제가 발생하고 있습니다:

1. **Context Pollution (문맥 오염)**: 특정 문서(예: Apple Inc.)를 요약해달라는 요청에도, 동음이의어 문서(예: 사과 과일)나 과거 대화의 잔재가 검색되어 답변에 섞여 들어갑니다.
2. **Ambiguity (지시어 모호성)**: "이거 요약해줘"와 같이 지시 대명사가 포함된 질문이 들어올 때, 엉뚱한 문서를 참고하여 답변합니다.

이 문제를 해결하기 위해 **검색 범위를 특정 소스(Source)로 제한**할 수 있는 메커니즘이 필요합니다.
이는 [RAG Strategy](../../docs/design_guides/005-llm-rag-strategy.md)에서 정의한 **"System Layer(Execution & Enforcement)"**의 핵심 기능을 구현하는 것입니다. 즉, LLM의 결정이나 사용자의 선택을 시스템 레벨에서 물리적으로 강제하여 문맥을 통제합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Metadata Filtering**: `DocumentRepository.search` 메소드는 `filters` 인자를 받아 특정 `doc_id` 또는 `source_url`을 가진 청크만 검색해야 합니다.
2. **Multi-Value Support**: 단일 값뿐만 아니라 **리스트 형태의 다중 값(OR 조건)**도 지원해야 합니다 (예: `doc_A`와 `doc_B`를 동시에 비교).
3. **Unified Filter Interface**: Hybrid Search(Neo4j + Chroma) 양쪽 모두에 동일한 필터 로직이 적용되어야 합니다.
4. **Admin UI Support**: RAG Playground에서 문서를 **다중 선택(Multi-select)**할 수 있어야 하며, 선택된 문서 내에서만 대화가 이루어져야 합니다.

### Non-Functional Requirements
1. **Strict Context Isolation**: 필터가 적용된 경우, 대화 이력(History)이 있더라도 필터링된 문서 외의 정보는 절대 답변에 포함되어서는 안 됩니다.
2. **Performance**: 필터 적용 시 쿼리 성능 저하가 없어야 하며(인덱스 활용), 기존 전체 검색 기능은 유지되어야 합니다.

## ✅ Definition of Done
1. `DocumentRepository`가 단일/다중 필터를 완벽히 지원.
2. RAG Playground에서 문서 선택에 따른 답변 변화가 검증됨.
3. **3대 검증 시나리오(Homonym, Context Switch, Source Injection)**를 통과하는 통합 테스트 구현.
