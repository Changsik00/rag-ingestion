# Walkthrough: Spec-066 Enhanced Trace Viewer

Spec 066에서는 RAG 파이프라인의 Rerank 투명성을 확보하기 위해 상세 로그 수집 및 시각화 기능을 구현했습니다.

## 📋 Changes Implemented
- [x] **RAGResult & Graph State 확장**: `rerank_log` 필드 추가 및 데이터 매핑 로직 구현.
- [x] **Rerank Node 로직 업데이트**: Pointwise Reranking 과정에서 개별 청크의 점수, 사유, 상태(Passed/Dropped) 수집.
- [x] **Admin UI 시각화**: 'Rerank Analysis' 전용 탭 추가 및 데이터프레임 기반 테이블 렌더링.
- [x] **UI 탐색성 개선**: RAG Playground에서 Trace Viewer로 즉시 이동할 수 있는 바로가기 링크 구현.

## 🧪 Verification Results

### 1. Automated Tests
- **Command:** `uv run pytest tests/unit/application/services/test_rag_dto.py`
- **Result:** ✅ Passed
- **Log Summary:**
```text
collected 1 item
tests/unit/application/services/test_rag_dto.py . [100%]
1 passed in 0.88s
```

### 2. Manual Verification (Scenarios)

#### 시나리오 1: Admin UI를 통한 엔드투엔드 확인 (가장 추천하는 방법)
1. **RAG Playground** (`/RAG_Playground`) 접속.
2. 질문(예: "Steve Jobs의 부모는 누구인가?")을 입력하고 답변을 기다립니다.
3. 답변 하단에 생성된 **"🔍 View Rerank Analysis"** 버튼을 클릭합니다.
4. 자동으로 **Observability & Trace** 페이지로 이동하며, `thread_id`가 입력된 상태로 'Rerank Analysis' 탭이 활성화됩니다.
5. 테이블에서 어떤 청크가 높은 점수를 받았고, 어떤 청크가 왜 탈락(`dropped`)했는지 확인합니다.

#### 시나리오 2: Trace Viewer에서 직접 조회 (ID를 알 때)
1. **Observability & Trace** (`/Observability_&_Trace`) 접속.
2. `Target System`을 `RAG Session`으로 선택.
3. 확인하고자 하는 `thread_id` (예: `playground-xxxx`)를 입력하고 `Fetch State` 클릭.
4. **'Rerank Analysis'** 탭을 클릭하여 상세 로그를 확인합니다.

#### 시나리오 3: Raw State 데이터 확인 (개발자용)
1. 위와 동일하게 Fetch State 수행 후 **'Raw Data'** 탭 클릭.
2. JSON 트리에서 `values.rerank_log` 항목을 찾아 데이터가 스키마에 맞게 들어있는지 확인합니다.

### 3. Evidence
- [x] **Admin UI 캡처**: Rerank Analysis 탭에서 Status, Score, Reasoning, Content Snippet이 포함된 테이블 확인.
- [x] **API Response**: `rerank_log`에 `chunk_id`, `source`, `content`(100자 요약)가 포함됨을 확인.

## 🔍 Key Findings (Optional)
- Dropped Chunks의 본문을 100자로 제한함으로써, 수십 개의 청크가 탈락하더라도 전체 State 크기가 비대해지는 것을 방지했습니다 (Cost & Latency 최적화).
