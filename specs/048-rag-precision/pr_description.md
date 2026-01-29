# feat(spec-048): rag precision refinement

## 📋 Summary

### 배경 및 목적
현재 RAG 시스템에서 사용자 질문과 관련이 적은 정보가 유사도 점수만으로 상위에 노출되어 답변 품질을 저하시키는 "과응답" 문제를 해결하기 위해 도입되었습니다. 검색된 청크를 LLM이 다시 평가하는 **Reranker** 과정을 추가하여 답변의 정밀도를 극대화합니다.

### 주요 변경 사항
- [x] **LLM Reranker Node 도입**: `RAGNodes.rerank_results`를 통해 검색 결과의 관련성을 1~10점으로 재평가.
- [x] **유사도 임계값 필터링**: 리랭킹 결과가 `min_relevance_score(5)` 미만인 청크를 컨텍스트에서 배제.
- [x] **Dynamic Context Window**: 고득점 청크로만 컨텍스트를 재구성하여 LLM에게 전달 (인용 정확도 향상).
- [x] **RAGGraphState 확장**: `reranked_chunks`, `rerank_log` 필드 추가로 리랭킹 과정 가시성 확보.
- [x] **Workflow 최적화**: `retrieve_hybrid` -> `rerank_results` -> `generate_answer`로 이어지는 파이프라인 완성.

## 🎯 Key Review Points
1. **Reranking Logic**: `rerank_results` 노드에서 상위 10개 청크에 대해 병렬로 LLM 평가를 수행하며, 지연 시간을 최소화하기 위해 `asyncio.gather`를 사용했습니다.
2. **Context Fallback**: 리랭킹 결과가 없거나 실패할 경우를 대비하여 `generate_answer` 노드에서 기존 청크를 사용하도록 안전장치를 마련했습니다.
3. **Prompt Efficiency**: `RERANKER_PROMPT`를 통해 각 청크의 점수와 이유를 JSON 형식으로 명확히 추출합니다.

## 🧪 Verification

### Automated Tests
```bash
# Reranker 노드 및 통합 팩 흐름 검증
uv run pytest tests/unit/test_rag_reranker.py tests/integration/test_rag_precision.py
```
**테스트 결과 요약:**
- ✅ `test_rerank_results_success`: 통과 (점수 기반 필터링 및 정렬 확인)
- ✅ `test_rag_precision_refinement_flow`: 통과 (전체 그래프 흐름 및 노이즈 차단 확인)

### Manual Verification (Scenarios)
1. **무관한 질문 차단**: "릭롤 노래" 질문 시 관련 없는 기술 문서가 검색되더라도, Reranker가 낮은 점수를 부여하여 최종 답변 컨텍스트에서 제외됨을 확인.
2. **정밀 인용 확인**: 복합적인 질문에 대해 가장 관련성이 높은 청크 상위 리스트만 인용되어 답변이 생성됨을 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/prompts/reranker.py`: 리랭커 전용 프롬프트 정의
- `tests/unit/test_rag_reranker.py`: Reranker 노드 단위 테스트
- `tests/integration/test_rag_precision.py`: 정밀도 개선 통합 테스트

### 🛠 Modified Files
- `app/domain/rag/state.py` (+8, -0): RAGGraphState에 리랭킹 관련 필드 추가
- `app/infrastructure/rag/nodes.py` (+115, -5): rerank_results 노드 구현 및 generate_answer 조정
- `app/infrastructure/rag/graph.py` (+2, -1): 그래프 워크플로우에 rerank_results 노드 추가
- `backlog/queue.md` (+1, -0): Spec 048 상태 업데이트

**Total:** 7 files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
