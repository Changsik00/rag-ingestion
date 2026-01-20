# Spec 022: Human-in-the-loop (Checkpointer)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 Logic Resolver(Spec 021)는 검증 실패 시 자동으로 재시도(Retry) 및 전략 수정(Backtracking)을 수행합니다. 그러나 단순히 자동화된 로직만으로는 해결할 수 없는 문제(예: 모호한 문맥, 반복적인 환각)가 발생할 수 있습니다.

이 경우 무한 루프를 방지하고 추출 품질을 보장하기 위해 **시스템이 실행을 멈추고 사용자의 판단(승인 또는 수정)을 요청하는 메커니즘(Human-in-the-loop)**이 필요합니다. 이를 위해 LangGraph의 `Checkpointer` 기능을 도입하여 상태를 저장하고, 특정 조건에서 실행을 중단(`interrupt`) 및 재개(`resume`)할 수 있어야 합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **Checkpointer 통합**: `LangGraph` 컴파일 시 `MemorySaver`(또는 영속적 저장소)를 `Checkpointer`로 설정하여 그래프 실행 상태를 저장해야 합니다.
2.  **Human Review Node 추가**: 검증 실패 시 기계적 해결(Logic Resolver)로 바로 넘어가는 대신, 특정 조건(예: 중요 오류, 재시도 한계 임박)에서 `human_review` 단계로 진입해야 합니다.
3.  **Interrupt 메커니즘**: `human_review` 노드 진입 전 실행을 중단(`interrupt_before`)하고, 외부(API/사용자)에서 상태를 확인하고 수정할 수 있어야 합니다.
4.  **State Update & Resume**: 사용자가 상태(예: `metadata`, `next_strategy`)를 수정한 후, 그래프 실행을 해당 시점부터 재개할 수 있어야 합니다.

### Non-Functional Requirements
1.  **Stateless API 지원**: HTTP 요청 간 상태 유지를 위해 `thread_id`를 활용해야 합니다.
2.  **Existing Logic Compatibility**: 기존의 `extract` -> `validate` -> `resolve` 흐름을 방해하지 않으면서 선택적으로 개입해야 합니다.

## ✅ Definition of Done
1.  `IngestionGraphBuilder`에 `checkpointer` 설정이 적용되어야 합니다.
2.  조건부 엣지(Conditional Edge)에서 `human_review`로 라우팅되는 로직이 구현되어야 합니다.
3.  단위/통합 테스트에서 `thread_id`를 사용하여 그래프를 멈추고, 상태를 수정한 뒤 재개하는 시나리오가 통과해야 합니다.
