# Walkthrough: Spec 020 Transition to LangGraph

## 1. Changes Overview
본 작업은 Ingestion Pipeline의 오케스트레이션 엔진을 LangChain(`RunnableSequence`)에서 **LangGraph(`StateGraph`)**로 교체하는 아키텍처 전환입니다.

### 1.1 Architecture Shift
> 상세한 결정 배경은 [docs/architecture_decisions/001_dag_to_graph_transition.md](../../docs/architecture_decisions/001_dag_to_graph_transition.md)를 참고하세요.

- **Before**: Linear DAG (Chain) - 입력에서 출력으로 데이터가 단방향 흐름.
- **After**: Stateful Graph - `IngestionState`를 공유하며 노드들이 상태를 갱신.

### 1.2 Key Components Implemented
| Component | Description |
| :--- | :--- |
| `IngestionState` | 파이프라인의 핵심 데이터 구조 (TypedDict). 모든 노드가 이를 공유합니다. |
| `IngestionNodes` | `extract_metadata`, `validate_content` 등 각 단계의 로직을 수행하는 함수 집합. |
| `IngestionGraph` | StateGraph를 정의하고 컴파일하는 빌더. Phase 1에서는 선형 흐름(`Extract` -> `Validate`)으로 구성. |
| `LangGraphAdapter` | Service Layer와 Graph 사이의 어댑터. 기존 `LLMInterface`를 준수하며 내부적으로 Graph를 실행. |

## 2. Test Evidence

### 2.1 Unit Tests (New Components)
LangGraph의 구성 요소들이 정상 작동함을 확인했습니다.
- `test_ingestion_state.py`: State 구조 검증 ✅
- `test_graph_nodes.py`: 각 노드의 비즈니스 로직(LLM 호출 및 State 갱신) 검증 ✅
- `test_ingestion_graph.py`: Graph 빌드 및 컴파일 성공 여부 검증 ✅

### 2.2 Integration Tests (Regression)
기존 시스템과의 호환성을 검증했습니다.
- `test_langgraph_adapter.py`: Adapter가 Graph를 실행하고 `ExtractedMetadata`를 올바르게 반환하는지 확인 ✅
- `test_success_flows.py`: **End-to-End Pipeline Verification**. API 호출부터 DB 저장까지 기존 기능이 100% 동일하게 동작함을 입증 ✅

```bash
# E2E Test Result
tests/integration/bdd/test_success_flows.py ..  [100%]
2 passed
```

## 3. Validation
서버가 정상 구동되며, 그래프 실행 로그가 정상적으로 출력됩니다.

1.  `extract_metadata` 노드 실행 -> `extract_metadata` 히스토리 추가
2.  `validate_content` 노드 실행 -> `validate_content` 히스토리 추가
3.  최종 결과(Metadata) 반환 성공

이로써 Phase 4의 복잡한 워크플로우(순환, 조건부 실행)를 수용할 준비가 완료되었습니다.
