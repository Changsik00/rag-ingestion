# Implementation Plan: Spec-066

## 📋 Branch Strategy
- `feature/066-enhanced-trace-viewer`

## 🛑 User Review Required
> [!IMPORTANT]
> - **데이터 크기 제약**: 탈락한 모든 청크의 전문을 저장하면 인메모리 State 및 API 응답이 커질 수 있습니다. 본문은 요약(첫 100자)만 저장하는 방식을 적용했습니다.
> - **보안**: 로그에 포함된 텍스트가 민감 정보를 포함할 수 있으므로, Admin 권한이 있는 경우에만 상세 로그가 노출되도록 설계합니다.

## 🎯 Core Strategy
## 🚨 Critical Issue: Data Contamination & Debug Reliability (Spec 066 Fix)
사용자 리포트에 따르면 세션 간 데이터 오염(Steve Jobs/Elon Musk 내용이 섞임) 및 디버그 정보의 부정확성이 발견되었습니다. 

### 🛠 Root Cause & Fix Strategy
1. **Reranker Crash**: `rag_nodes.py`에서 `config` 인자 전달 오류로 Reranker가 작동하지 않고 항상 0점을 반환하여 필터링 기능이 상실됨. (수정 완료)
2. **Fallback Leakage**: 검색 결과가 없을 때 필터를 완전히 제거하고 전역 검색을 수행하여 관련 없는 유명인(Elon Musk 등) 데이터가 유입됨.
3. **Intent Classifier Missing Targets**: "어쩌다 어른"과 같은 고유 명사를 Target으로 인식하지 못해 필터가 빈 값으로 설정됨.

### Architecture Context
Rerank 과정의 상세 데이터를 수집하여 `RAGGraphState`를 통해 최종 `RAGResult`까지 전달합니다.

| Component | Strategy | Reasoning |
|:---:|:---|:---|
| **Domain** | `RAGResult` 필드 추가 | 클라이언트(API/UI) 전달용 계약 |
| **LangGraph State** | `rerank_log` 리스트 추가 | 노드 간 데이터 전달 및 영속화 |
| **State Merging** | `Annotated[list, lambda x, y: y]` | 리스트 중복 누적 방지(덮어쓰기) |
| **RAG Nodes** | Rerank 로직 수정 | 로그 생성 지점 |
| **Admin UI** | Streamlit Component 추가 | 사용자 시각화 |

## 📂 Proposed Changes

### [Domain & Application Layer]

#### [MODIFY] `app/domain/value_objects/rag_state.py`
- `rerank_log` 타입을 `Annotated[list[dict], lambda x, y: y]`로 변경하여 새로운 로그가 발생할 때마다 이전 로그를 덮어쓰도록 처리.

#### [MODIFY] `app/infrastructure/ai/rag_nodes.py`
- `_get_rerank_score`에서 `agenerate` 호출 시 `config` 인자 제거 (완료).
- `retrieve_hybrid`에서 Fallback 시에도 **최소한의 컨텍스트(세션 주제)**는 유지하도록 로직 보강.
- `rerank_results` 메서드에서 `rerank_log` 수집 로직 구현.
- 탈락한 청크의 `content`를 100자로 Truncate.

#### [MODIFY] `app/application/services/agent.py`
- `AgentState`에 `rerank_log` 필드 추가.
- `search_node`에서 `rag_service.retrieve_and_generate` 결과를 `context_data`에 담을 때 `rerank_log` 포함.

#### [MODIFY] `app/domain/services/intent_classifier.py`
- "어쩌다 어른" 등 고유 프로그램/문서 제목을 `targets`로 더 잘 추출하도록 프롬프트 고도화.

### [Admin Layer]

#### [MODIFY] `admin/pages/3_Observability_&_Trace.py`
- 'Rerank Analysis' 탭 추가 및 Pandas DataFrame 기반 테이블 렌더링.

#### [MODIFY] `admin/pages/4_RAG_Playground.py`
- 결과 하단에 `Observability_&_Trace` 페이지로 이동하는 링크 추가.

## 🧪 Verification Plan

### Automated Tests
```bash
# RAGResult DTO 검증
uv run pytest tests/unit/application/services/test_rag_dto.py
```

### Manual Verification
1. RAG Playground에서 질문 수행.
2. 결과 하단의 "🔍 View Rerank Analysis" 버튼 클릭하여 이동.
3. Observability 페이지에서 'Rerank Analysis' 탭이 데이터와 함께 정상 표시되는지 확인.
4. **중복 로그 확인**: 동일 세션(`thread_id`)에서 여러 번 질문을 던졌을 때, `rerank_log`가 이전 질문의 로그와 합쳐지지 않고 현재 질문의 로그만 필터링되어 중복 없이 나오는지 확인.
