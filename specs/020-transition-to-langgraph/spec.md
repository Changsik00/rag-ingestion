# Spec 020: Transition to LangGraph

## 📋 배경 및 문제 정의 (Background & Problem)

### 히스토리 및 결정 배경 (History & Decision Rationale)
본 프로젝트는 초기 MVP부터 단계적으로 발전해왔으며, 현재 아키텍처는 다음과 같은 한계에 봉착했습니다.

1.  **Spec 001 ~ 004 (Foundation)**: 초기에는 단순한 HTTP 요청 처리와 `BackgroundTasks`를 이용한 비동기 작업으로 충분했습니다. 하지만 작업 실패 시 "어느 단계에서 죽었는지" 파악하기 어렵고, 재시도가 불가능했습니다.
2.  **Spec 005 (LangChain 도입)**: `RunnableSequence`를 도입하여 추출 파이프라인(Extract -> Summary -> Entities)을 구조화했습니다. 선형적인 작업에는 효과적이었으나, 유연성이 부족했습니다.
3.  **Phase 4의 요구사항 (Advanced Workflow)**:
    *   **Conditional Logic**: 특정 조건(예: 뉴스 기사)에만 추가 추출 실행.
    *   **Cycles & Loops**: 품질이 낮으면 다시 요약하거나, 정보가 부족하면 추가 검색.
    *   **Human-in-the-loop**: 중요 데이터는 사람이 검수 후 저장.

기존 LangChain의 Chain 방식(DAG)으로는 이러한 순환 및 상태 기반 로직을 구현하기 복잡합니다. 따라서, 파이프라인을 **상태 머신(State Machine)**으로 모델링할 수 있는 **LangGraph**로 전환하기로 결정했습니다.

### 문제 정의 (Problem Statement)
*   **상태 공유의 어려움**: Chain 간 데이터를 넘길 때 입/출력 스키마 맞추기가 번거로움.
*   **유연성 부족**: 실행 도중 동적으로 경로를 변경하거나 반복(Loop)하기 어려움.
*   **확장성 한계**: 향후 계획된 "Logic Resolver"나 "Automated Trigger"를 수용하기엔 현재 구조가 너무 정적임.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **State-driven Architecture**: `IngestionState`를 정의하고, 모든 노드가 이 상태를 공유/갱신해야 함.
2.  **Graceful Migration**: 기존 `LangChainAdapter`의 기능을 완전히 대체하며, 외부(Service Layer)에서는 변경을 인지하지 못해야 함.
3.  **Basic Graph Flow**: `Extract` -> `Transform` -> `Load` (저장은 Service에서 하더라도 데이터 준비까지) 흐름을 그래프로 구현.

### Non-Functional Requirements
1.  **Maintainability**: 노드(Node) 단위로 로직이 분리되어 테스트가 쉬워야 함.
2.  **Scalability**: 추후 Human-in-the-loop 단계 추가가 용이해야 함.

## ✅ Definition of Done
1.  `IngestionState` TypedDict 정의 및 검증 테스트 통과.
2.  LangGraph 기반의 `IngestionGraph` 구현 및 단위 테스트 통과.
3.  기존 Integration Test(`test_success_flows.py`)가 수정 없이(또는 최소 수정으로) 통과.
4.  문서화: `docs/architecture_decisions/001_dag_to_graph_transition.md` 및 history 아카이빙 완료.
