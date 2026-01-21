# Spec-025: Contextual RAG (Query Rewriting)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 Admin Dashboard의 RAG(검색 증강 생성) 기능은 **단발성(single-turn)** 검색 만을 지원합니다. 사용자가 이전에 질문한 내용이나 "그것은?", "그 사람은?"과 같은 대명사를 사용하여 후속 질문을 할 경우, 문맥을 파악하지 못하고 독립적인 질문으로 처리하여 관련 없는 검색 결과를 반환합니다. 이로 인해 자연스러운 대화 흐름이 끊기고 검색 품질이 저하되는 문제가 있습니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Query Rewriting**: 사용자의 입력과 대화 히스토리를 분석하여, 검색에 적합한 "독립적인 쿼리(Standalone Query)"로 재구성해야 합니다.
2. **Conversation History Management**: Playground 내에서 사용자의 대화 기록을 유지하고 관리(최근 N 턴)해야 합니다.
3. **Transparent Debugging**: 재구성된 쿼리가 무엇인지 사용자가 확인할 수 있도록 Debug View에 표시해야 합니다.

### Non-Functional Requirements
1. **Low Latency**: Query Rewriting 과정이 전체 응답 시간을 크게 저해하지 않아야 합니다.
2. **Robustness**: 히스토리가 없거나 모호하지 않은 질문은 원본 그대로 검색되어야 합니다.

## ✅ Definition of Done
1. 사용자가 대명사(그, 그녀, 이것)를 사용하여 질문했을 때 올바른 엔티티 정보를 검색해야 합니다.
2. Playground의 `🛠️ Debug` 창에서 재구성된 쿼리를 확인할 수 있어야 합니다.
3. `tests/unit/domain/test_query_rewriter.py` 테스트가 모두 통과해야 합니다.
