# Implementation Plan: Spec-025

## 📋 Branch Strategy
- `feature/spec-025-contextual-rag`

## 🛑 User Review Required
- [x] 없음 (기능 개선 요청 사항)

## 🎯 Core Strategy
- **Domain Service 분리**: `QueryRewriter`를 별도 도메인 서비스로 구현하여 LLM 의존성을 캡슐화하고 컨트롤러(UI) 로직을 단순하게 유지합니다.
- **LLM 재사용**: 별도의 모델 인스턴스를 생성하지 않고, 기존 `LLMInterface`를 재사용하되 프롬프트만 변경하여 리소스를 절약합니다.
- **Stateless Service**: `QueryRewriter` 자체는 상태를 가지지 않고, 호출 시점의 `history`를 인자로 받아 처리합니다. 상태 관리는 `st.session_state`가 담당합니다.

## 📂 Proposed Changes

### Domain Layer

#### [NEW] `app/domain/services/query_rewriter.py`
LLM을 사용하여 대화 흐름에 맞는 검색 쿼리를 생성합니다.
```python
class QueryRewriter:
    def rewrite(self, query: str, history: list[dict]) -> str:
        # Construct prompt with history
        # Invoke LLM
        # Return rewritten query
```

### Presentation Layer (Admin)

#### [MODIFY] `app/admin/pages/4_RAG_Playground.py`
Playground에 Rewriting 로직을 통합합니다.
```python
# Before
chunk = repo.search(prompt)

# After
rewriter = QueryRewriter(llm)
standalone_query = rewriter.rewrite(prompt, st.session_state.messages[-5:]) # 최근 5턴
chunk = repo.search(standalone_query)
```

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests
uv run pytest tests/unit/domain/test_query_rewriter.py
```

### Manual Verification
1. RAG Playground 접속
2. "일론 머스크는 누구야?" 질문 (답변 확인 및 Debug View: Original Query 확인)
3. "그가 만든 회사는?" 질문
4. Debug View 확인: Rewritten Query가 "일론 머스크가 만든 회사는?"으로 변경되었는지 검증
5. 답변이 테슬라, 스페이스X 등을 포함하는지 확인
