# feat(spec-067): advanced reranking logic research

## 📋 Summary

### 배경 및 목적
- 현재 RAG 파이프라인의 Pointwise 리랭킹 방식은 정보가 여러 청크에 파편화되어 있을 때(Context Fragmentation), 각 청크를 독립적으로 평가하여 관련성이 낮다고 판단하고 탈락시키는 한계가 있습니다.
- 이를 해결하기 위해 여러 청크를 한꺼번에 분석하는 **Listwise Reranking**과 인접 맥락을 보강하는 **Context Window Expansion (Sliding Window)** 기법을 도입하여 검색 정밀도를 개선합니다.

### 주요 변경 사항
- [x] **Listwise Reranking 전략 구현**: 상위 N개 청크를 그룹화하여 LLM이 상대적 중요도를 비교하고 순위를 매기는 로직 추가.
- [x] **Context Window Expansion 도입**: 청크 평가 시 전후 인접 청크를 결합하여 정보 손실 방지.
- [x] **Neo4j Repository 확장**: 인접 청크 조회를 위한 `get_adjacent_chunks` 메서드 구현.
- [x] **State Management 고도화**: `RAGGraphState` 내 `rerank_strategy` 필드 추가를 통한 유연한 전략 전환 지원.

## 🎯 Key Review Points
1. **Listwise Logic**: `rag_nodes.py`의 `_rerank_listwise`에서 JSON Array 형태의 LLM 응답을 파싱하고 필터링하는 예외 처리 로직.
2. **Context Padding**: `_expand_context_window`에서 `[Pivotal Context]` 마커를 사용해 LLM이 중심 청크를 인식하게 한 설계.
3. **Neo4j Query**: `Neo4jDocumentRepository.get_adjacent_chunks`에서 `index` 범위를 이용한 효율적인 데이터 로드.

## 🧪 Verification

### Automated Tests
```bash
# Repository 단위 테스트
PYTHONPATH=. uv run python scripts/verify_spec_067.py
```
**테스트 결과 요약:**
- ✅ `get_adjacent_chunks`: 인접 청크 정상 로드 및 정렬 확인

### Manual Verification (Scenarios)
1. **시나리오 1 (Context Restoration)**:
    - **동작**: 정보가 두 청크로 쪼개진 문서(예: "프랑스의 수도는... (청크1)", "...파리이다. (청크2)")를 준비하고 질문을 던짐.
    - **결과 확인**: Trace Viewer에서 `rerank_strategy="listwise"` 작동 시, 청크2가 인접 맥락(청크1)을 포함하여 높은 점수로 유지(Passed)되는지 확인.
2. **시나리오 2 (Comparison Ranking)**:
    - **동작**: 유사한 내용을 담은 여러 청크들이 검색되었을 때 Listwise 모드로 실행.
    - **결과 확인**: LLM이 단순히 점수만 주는 것이 아니라, `reasoning` 필드에 다른 청크와의 상대적 비교 결과가 포함되는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/services/prompts/listwise_reranker.py`: Listwise 전용 프롬프트 정의
- `scripts/verify_spec_067.py`: 핵심 로직 검증 스크립트

### 🛠 Modified Files
- `app/domain/interfaces/document_repository.py` (+6, -1): `get_adjacent_chunks` 명세 추가
- `app/infrastructure/repositories/neo4j_document_repository.py` (+32, -0): 인접 청크 조회 로직 구현
- `app/infrastructure/ai/rag_nodes.py` (+149, -10): Listwise 및 Context Expansion 로직 통합
- `app/domain/value_objects/rag_state.py` (+3, -0): `rerank_strategy` 필드 추가

**Total:** 6 files changed (including specs/task)

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
