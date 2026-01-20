# Spec 020: Transition to LangGraph

## 📋 배경 및 문제 정의 (Background & Problem)

> **Note**: 본 Spec의 상세한 결정 히스토리는 [docs/history/020-decision-record.md](../../docs/history/020-decision-record.md)로 이동되었습니다.

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
