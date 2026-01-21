# Walkthrough: Spec-025 Contextual RAG

## 1. 개요 (Overview)
본 워크스루는 **Spec 025 (Contextual RAG)**의 구현 결과 및 검증 과정을 기록합니다. RAG Playground에서 멀티턴 대화가 가능해졌으며, 대명사를 포함한 모호한 질문이 자동으로 명확한 쿼리로 변환되는 것을 확인했습니다.

## 2. 변경 사항 (Changes)
### 2.1 Query Rewriter Service
- **파일**: `app/domain/services/query_rewriter.py`
- **기능**: 대화 이력을 받아 LLM을 통해 독립적 쿼리 생성.

### 2.2 Playground UI
- **파일**: `app/admin/pages/4_RAG_Playground.py`
- **기능**:
    - 검색 전 `rewriter.rewrite()` 호출.
    - `🛠️ Debug` 섹션에 `Original` vs `Rewritten` 비교 표시.

## 3. 검증 결과 (Verification Results)

### 3.1 Unit Tests
`tests/unit/domain/test_query_rewriter.py` 통과.
- **Case 1 (Empty History)**: 원본 쿼리 즉시 반환 확인.
- **Case 2 (Context)**: "그의 형제는?" -> "일론 머스크의 형제는?" 변환 확인.

### 3.2 Manual Scenario
**시나리오**: 일론 머스크에 대한 연속 질문
1. **User**: "일론 머스크는 누구야?"
    - **Rewritten**: "일론 머스크는 누구야?" (히스토리 없음)
    - **Searching**: "일론 머스크는 누구야?"
2. **User**: "그가 설립한 회사는?"
    - **Rewritten**: "일론 머스크가 설립한 회사는 어디입니까?"
    - **Searching**: "일론 머스크가 설립한 회사는 어디입니까?"
    - **Result**: 테슬라, 스페이스X 등 관련 정보 검색 성공 확인.

## 4. Known Issues
- **Retrieval Quality**: 쿼리가 "일론 머스크의 고등학교는 어디입니까?"로 정확히 변환되어도, DB에 해당 정보(Ingested Chunk)가 없으면 답변할 수 없음 (Spec 026 해결 예정).
