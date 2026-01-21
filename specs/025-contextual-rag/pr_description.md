feat(spec-025): contextual rag query rewriting

## 📋 Summary
기존 RAG Playground의 단발성(Single-turn) 검색 방식을 개선하여, **멀티턴(Multi-turn) 대화**를 지원하도록 변경했습니다.
사용자의 대화 이력(History)을 바탕으로 모호한 질문(예: "그는?")을 **독립적인 검색 쿼리(Standalone Query)**(예: "일론 머스크는?")로 재구성(Rewriting)하는 `QueryRewriter` 서비스를 도입했습니다.

## 🎯 Key Review Points
1. **`QueryRewriter` 구현**: `app/domain/services/query_rewriter.py`에서 LLM 프롬프트가 대화 문맥을 적절히 반영하는지 확인해주세요.
2. **Playground UI 변경**: `app/admin/pages/4_RAG_Playground.py`에서 검색 전에 `rewriter.rewrite()`가 호출되는 흐름과 Debug View에 표시되는 정보가 직관적인지 확인 부탁드립니다.
3. **최적화**: 비용 절감을 위해 히스토리가 없는 경우 LLM을 호출하지 않고 원본 쿼리를 반환하도록 처리했습니다. (`tests/unit/domain/test_query_rewriter.py` 참조)

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests for QueryRewriter
uv run pytest tests/unit/domain/test_query_rewriter.py
```

### Manual Verification
1. Playground 접속 (`streamlit run app/admin/dashboard.py`)
2. 질문: "일론 머스크가 누구야?" (원본 검색 확인)
3. 후속 질문: "그가 만든 회사는?" (자동으로 "일론 머스크가 만든 회사는?"으로 변환되는지 Debug View에서 확인)
4. 답변 품질: 테슬라 등 관련 정보가 검색되어 답변에 포함되는지 확인

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/query_rewriter.py`: 대화 이력을 기반으로 쿼리를 재구성하는 도메인 서비스
- `tests/unit/domain/test_query_rewriter.py`: QueryRewriter 단위 테스트

### 🛠 Modified Files
- `app/admin/pages/4_RAG_Playground.py` (+37, -7): Playground에 Query Rewriting 로직 통합 및 Debug View 개선 inside loop

**Total:** 3 files changed

## ✅ Definition of Done
- [x] 대명사가 포함된 후속 질문이 올바른 엔티티 명칭으로 치환되어야 한다.
- [x] Playground Debug View에서 `Original` vs `Rewritten` 쿼리를 비교할 수 있어야 한다.
- [x] 단위 테스트 통과 (Pass)
