# Walkthrough - Spec 034: RAG Pipeline Recovery & Stability

## 개요
RAG 파이프라인의 검색 안정성을 높이고 할루시네이션을 방지하기 위한 개선 작업을 완료했습니다.
특히 엄격한 필터링으로 인해 결과가 없는 경우를 자동으로 처리하는 Fallback 로직과, LLM의 근거 없는 답변을 억제하는 가드레일을 도입했습니다.
또한, `AsyncSqliteSaver`를 통한 세션 보존 최적화 및 사고 과정(Reasoning Trace) 시각화 기능을 구현했습니다.

## 주요 변경 사항

### 1. Adaptive Retrieval (Fallback Logic)
- **노드**: `retrieve_hybrid` (in `app/infrastructure/rag/nodes.py`)
- **내용**: 사용자가 지정한 필터(문서 ID 등)로 검색 결과가 없을 경우, 자동으로 필터를 해제하고 전역 검색을 수행합니다.
- **UI**: Fallback이 발생하면 Playground 상단에 노란색 경고로 사용자에게 알립니다.

### 2. Hallucination Guardrails
- **노드**: `generate_answer` (in `app/infrastructure/rag/nodes.py`)
- **내용**: LLM 프롬프트에 `CRITICAL RULES`를 추가하여, 제공된 컨텍스트에 없는 내용은 명확히 답변을 거부하도록 강제했습니다.

### 3. Reasoning Trace Visualization
- **상태**: `reasoning_log` 필드 추가 (in `app/domain/rag/state.py`)
- **기능**: 파이프라인의 각 단계(의도 분류, 필터링, 검색, 답변 생성)에서 LLM이 내린 판단 근거를 로그로 남기고, Playground의 전용 디버그 UI에서 실시간으로 확인할 수 있습니다.

### 4. Async Checkpointer Optimization (Hotfix)
- **인프라**: `AsyncSqliteSaver` + `aiosqlite` 도입 (in `app/interfaces/api/dependencies.py`)
- **안정성**: 기존 동기식 `SqliteSaver`에서 발생하던 `SqliteSaver does not support async methods` 에러를 해결하고, 대화 내역 영구 보존 기능을 안정화했습니다.

## 검증 결과

### 자동 테스트
- `tests/unit/infrastructure/rag/test_rag_nodes.py`: Fallback 및 Reasoning Logging 검증 (7/7 Passed)
- `tests/integration/bdd/test_human_loop.py`: Async Checkpointer 및 HITL flow 검증 (Passed)
- 전체 통합 테스트 (204개): 완료

### 수동 검증
- **Fallback**: 무관한 필터 적용 후 질문 시 전역 검색 결과로 답변 생성 확인
- **Reasoning**: Playground 디버그 UI에서 "🧠 [Intent]", "📚 [Context]" 등 단계별 사고 과정 출력 확인
- **Persistence**: 새로고침 후에도 이전 대화 내역 및 디버그 정보 유지 확인

## 📋 Testing Playbook (검증 매뉴얼)
리뷰어가 실제 환경에서 기능을 검증하기 위한 단계별 가이드입니다.

### Step 1: 지식 수집 (Ingestion)
*   **프롬프트**: `이 기사 내용 좀 수집해줄래? https://n.news.naver.com/mnews/article/001/0015185960`
*   **기대 결과**: `AdminAgent`가 'ingest' 인텐트를 감지하고 수집을 시작합니다. 완료 시 "✅ 수집 완료" 메시지가 나타납니다.

### Step 2: HITL 활성화 (Sidebar)
*   Playground 왼쪽 사이드바 하단의 **`Advanced Settings`**를 확장합니다.
*   **`Enable HITL Review`** 토글을 **ON**으로 변경합니다. (이때부터 답변 생성 전 시스템이 중단됩니다.)

### Step 3: 질문 및 인터럽트 확인
*   **프롬프트**: `방금 수집한 기사에서 주요 내용은 뭐야?`
*   **기대 결과**: 
    1.  상태 표시줄에 "🤖 Detecting intent..." 가 표시됩니다.
    2.  화면에 대답 대신 **`🚦 Paused for Human Review`** 경고가 나타납s니다.
    3.  하단에 **`✅ Confirm & Generate Answer`** 버튼이 생성됩니다.

### Step 4: Trace Viewer & HITL Control 확인
*   Playground에서 버튼을 누르기 전, 사이드바 메뉴들을 확인합니다.
*   **Trace Viewer**: `Thread ID`에 `playground-default`를 입력하면 현재 멈춰있는 지점까지의 사고 과정 로그가 출력됩니다.
*   **HITL Control**: 현재 멈춰있는 "Active Threads" 목록에 세션이 나타나며, 여기서 'Resume'을 실행할 수도 있습니다.

### Step 5: 답변 생성 완료
*   Playground로 돌아와 **`✅ Confirm & Generate Answer`** 버튼을 클릭하여 답변이 최종 생성되는지 확인합니다.

## 향후 과제
- 지식 그래프 데이터가 부족할 경우에 대한 추가적인 Fallback 전략 고도화 (Spec 035 예정)
