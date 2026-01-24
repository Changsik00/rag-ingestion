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

## 향후 과제
- 지식 그래프 데이터가 부족할 경우에 대한 추가적인 Fallback 전략 고도화 (Spec 035 예정)
