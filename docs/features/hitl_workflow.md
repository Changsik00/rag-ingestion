# Human-in-the-loop (HITL) Workflow

## 1. 개요 (Overview)
**Human-in-the-loop (HITL)**는 자동화된 파이프라인(Ingestion) 실행 중 발생할 수 있는 모호하거나 위험한 상황에서 시스템이 실행을 멈추고(**Interrupt**), 사람의 판단(**Review**)을 통해 수정하거나 승인한 후 다시 실행(**Resume**)하는 메커니즘입니다.

이 시스템은 `LangGraph`의 `Checkpointer` 기능을 사용하여 상태를 관리하며, 사용자는 API를 통해 멈춰있는 작업(Thread)의 상태를 조회하고 수정할 수 있습니다.

## 2. 핵심 개념 (Core Concepts)

### Interrupt (일시 정지)
- LLM 또는 시스템 로직이 판단하기 어려운 상황(예: 낮은 신뢰도, 재시도 초과)에서 `human_review` 노드 진입 직전에 실행을 멈춥니다.
- 이 상태에서 작업은 메모리(또는 DB)에 저장된 채 대기합니다.

### Review (검토 및 수정)
- 사용자는 현재 멈춰있는 상태(`State`)를 조회합니다.
- 잘못된 데이터(예: 오분류된 Entity Type)나 설정(예: Strict Mode 해제)을 수정합니다.

### Resume (재개)
- 사용자가 수정 또는 승인(`null` 수정)을 완료하면, 멈췄던 시점부터 그래프 실행이 다시 시작됩니다.
- 수정된 `State`를 기반으로 다음 로직(Logic Resolver 등)이 수행됩니다.

## 3. Workflow Diagram

```mermaid
graph TD
    A[Start Ingestion] --> B[Extract Metadata]
    B --> C[Validate Content]
    
    C -- Pass --> D[Save & End]
    C -- Fail --> E{Critical Error?}
    
    E -- No (Retry) --> F[Logic Resolver]
    E -- Yes (Interrupt) --> G[🛑 human_review]
    
    G -.-> |User Action| H((Human Review))
    
    H -- Update State --> I[Resume Graph]
    I --> F (Resolved Logic with New State)
    F --> B (Re-extraction)
```

## 4. 사용자 행동 가이드 (User Actions)

### 상황 A: 데이터가 잘못된 경우 (Correction)
- **상황**: LLM이 회사명을 사람으로 잘못 추출함.
- **행동**: `metadata`의 `entities` 리스트를 직접 수정하여 업데이트.
- **결과**: 수정된 Entity 정보로 그래프가 재개됨.

### 상황 B: 기준이 너무 엄격한 경우 (Relaxation)
- **상황**: 내용 검증이 실패했으나, 사용자가 보기엔 허용 가능함.
- **행동**: `active_constraints.strict_mode`를 `false`로 변경하거나, `error` 필드를 비움.
- **결과**: Logic Resolver가 완화된 기준으로 다시 검증하거나 통과시킴.

### 상황 C: 포기 (Abort)
- **상황**: 해당 문서는 수집 가치가 없거나 해결 불가능함.
- **행동**: 별도의 Resume 명령 없이 해당 `thread_id` 폐기 (또는 Cancel API 호출).
- **결과**: 작업 중단.
