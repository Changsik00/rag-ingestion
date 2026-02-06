# Implementation Plan: Spec-066

## 📋 Branch Strategy
- `feature/066-enhanced-trace-viewer`

## 🛑 User Review Required
> [!IMPORTANT]
> - **데이터 크기 제약**: 탈락한 모든 청크의 전문을 저장하면 인메모리 State 및 API 응답이 커질 수 있습니다. 본문은 요약(첫 100자)만 저장하는 방식을 적용했습니다.
> - **보안**: 로그에 포함된 텍스트가 민감 정보를 포함할 수 있으므로, Admin 권한이 있는 경우에만 상세 로그가 노출되도록 설계합니다.

## 🎯 Core Strategy
## 🚨 Root Cause Analysis: Data Contamination & Debug Failure
사용자 리포트에 기반한 심층 분석 결과, 다음과 같은 근본 원인이 파악되었습니다.

### 1. Retrieval Layer (리트리벌 레이어)
- **문제**: 벡터 검색(ChromaDB)에 **유사도 임계치(Similarity Threshold)**가 없어, 관련 문서가 없더라도 "가장 덜 먼" 무의미한 문서(스티브 잡스 등)를 무조건 반환함.
- **해결**: 검색 점수(`distance`)를 기반으로 일정 기준 이하의 청크는 원천 차단하는 로직 검토.

### 2. Orchestration Layer (오케스트레이션 레이어)
- **문제**: Intent Classifier가 대상을 찾지 못할 경우의 **Fallback(전역 검색)**이 너무 공격적임. 빈 필터로 검색 시 DB 내의 "인기 있는(Embedding 밀도가 높은)" 데이터가 유입됨.
- **해결**: Fallback 시에도 세션의 최소 문맥을 유지하거나, 검색 실패를 명시적으로 처리하도록 로직 보강.

### 3. LLM Layer (프롬프트 편향)
- **문제**: 시스템 프롬프트 및 예시(Examples)에 "스티브 잡스", "일론 머스크" 같은 특정 유명인이 포함되어 있어, 모델이 관련 없는 질문에서도 해당 정보를 억지로 주입하거나 별칭(Alias)으로 강제 변환하는 경향이 있음.
- **해결**: 모든 컴포넌트에서 특정 인물/기업 언급과 관련된 **강제 지침 및 예시를 완전히 제거**. 중립적인 기본 지침만 남기고 질문-문맥 불일치 시 거절(Refusal) 지침을 강화.

## 🧪 Neutralization & Verification Plan (Phase 3)
단순 수정을 넘어 시스템 전반의 중립성을 검증합니다.

### 1. Intent Classifier 정화 (삭제 중심)
- **Task**: `intent_classifier.py`에서 별칭 확장(Alias Expansion) 지침 자체를 삭제.
- **Goal**: 특정 인물로의 과도한 쿼리 확장을 방지하고 사용자의 원본 의도에 집중.

### 2. Reranker 엄격도 강화
- **Task**: `reranker.py`의 점수 기준 수정 (단순 주제 언급만으로는 높은 점수를 주지 않도록 조정).
- **Goal**: 노이즈 데이터가 상위권에 남는 확률 최소화.

### 3. Agent Router 예시 정화 (삭제 중심)
- **Task**: `agent.py`의 라우터 프롬프트 예시에서 특정 유명인 이름이 포함된 문장을 삭제.
- **Goal**: 에이전트 판단 과정에서 고정관념 개입 차단.

## 🧪 Diagnostic & Verification Plan (Phase 1)
코드를 수정하기 전, 다음 테스트를 통해 정교한 임계치와 로직을 도출합니다.

### 1. Temperature Analysis (온도별 비교)
- **Test**: "어쩌다 어른" 질문에 대해 Temp (0, 0.5, 1.0)를 적용하여 Reranker의 점수와 Reasoning이 어떻게 변하는지 로그를 통해 비교 분석.
- **Goal**: 노이즈 데이터에 대해 LLM이 얼마나 일관되게 낮은 점수를 주는지 확인.

### 2. Similarity Metric Audit (임계값 도출)
- **Test**: `scripts/debug_state_inspect.py`를 확장하여 ChromaDB의 실제 `distance` 값을 출력.
- **Goal**: "어쩌다 어른" vs "스티브 잡스"의 거리 차이를 수치화하여 최적의 Threshold 도출.

### 3. Prompt Bias Test
- **Test**: 시스템 프롬프트에서 특정 인물 예시를 제거한 버전과 유지한 버전의 답변 질 비교.

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
- "일론 머스크" 등 특정 인물에 편향된 Alias instruction 및 Examples 제거.
- "어쩌다 어른" 등 고유 프로그램/문서 제목을 `targets`로 추출하는 로직은 유지하되 중립성 강화.

#### [MODIFY] `app/application/services/agent.py`
- Router 프롬프트 예시에서 "Elon Musk" 등 특정 인물 언급 제거 및 일반 예시로 교체.

#### [MODIFY] `app/domain/services/prompts/reranker.py`
- 관련성 점수(7, 5점)에 대한 기준을 더 엄격하게 수정하여 단순 키워드 포함이 아닌 "질문에 대한 답변 가능성"을 우선하도록 변경.

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
