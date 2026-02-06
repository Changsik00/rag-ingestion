# feat(spec-066): enhanced trace viewer

## 📋 Summary

### 배경 및 목적
현재 RAG 파이프라인은 최종 답변 생성에 사용된 청크 정보만 제공하여, Reranking 과정에서 어떤 데이터가 왜 제외되었는지 알기 어렵습니다. 이를 개선하여 검색 품질 디버깅 효율을 높이고 파이프라인의 투명성을 확보하고자 합니다.

### 주요 변경 사항
- [x] **Domain 확장**: `RAGResult`에 `rerank_log` 필드 추가.
- [x] **Node 로직 개선**: Rerank 노드에서 상세 스코어링 사유 및 탈락 데이터 수집 (100자 요약).
- [x] **Admin 시각화**: Trace Viewer에 'Rerank Analysis' 전용 탭 추가.
- [x] **UX 개선**: RAG Playground에서 상세 트레이스로 바로 가기 버튼 추가.

## 🎯 Key Review Points
1. **Rerank Trace Data**: `RerankNode`에서 수집하는 데이터 항목(score, reasoning, content)의 적절성.
2. **Data Minimalism**: 탈락한 청크의 본문을 100자로 제한하여 State 크기를 관리하는 방식.
3. **UI Integration**: Playground에서 Trace Viewer로 `thread_id` 파라미터를 넘겨 유기적으로 연결하는 부분.

## 🧪 Verification

### Automated Tests
```bash
# RAGResult DTO 검증
uv run pytest tests/unit/application/services/test_rag_dto.py
```
**테스트 결과 요약:**
- ✅ `test_rag_result_contains_rerank_log`: 통과

### Manual Verification (Scenarios)
1. **시나리오 1: Playground 통합 확인 (추천)**
    - **동작**: RAG Playground에서 질문 입력 -> 결과 하단 "🔍 View Rerank Analysis" 버튼 클릭.
    - **결과**: Trace Viewer로 자동 이동 및 'Rerank Analysis' 탭 활성화 확인.
2. **시나리오 2: Trace Viewer 직접 확인**
    - **동작**: Observability 페이지에서 `RAG Session` 선택 -> `thread_id` 입력 -> Fetch State.
    - **결과**: 'Rerank Analysis' 탭에서 청크별 스코어 및 사유 테이블 표시 확인.
3. **시나리오 3: Raw State 데이터 확인 (개발자용)**
    - **동작**: Fetch State 후 'Raw Data' 탭 확인.
    - **결과**: `values.rerank_log`에 상세 객체 배열이 스키마대로 포함됨을 확인.

## 📦 Files Changed

### 🛠 Modified Files
- `app/application/services/rag.py`: RAGResult 필드 및 매퍼 수정.
- `app/infrastructure/ai/rag_nodes.py`: Rerank 로그 수집 로직 추가.
- `admin/pages/3_Observability_&_Trace.py`: Rerank Analysis 탭 시각화.
- `admin/pages/4_RAG_Playground.py`: 트레이스 링크 버튼 추가.

## ✅ Definition of Done
- [x] 모든 단위 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
