# Spec 041: Admin HITL UI & Robustness (Follow-up)

## 1. Background
Spec 040(Verification Script) 수행 과정과 이전 Spec 022(HITL) 구현 과정에서, Admin Dashboard(Streamlit)의 UX가 사용자가 작업을 중단하고 재개하기에 직관적이지 않다는 문제가 발견되었습니다.
또한, Checkpointer의 `thread_id`가 충돌할 가능성이 제기되어 이에 대한 구조적 해결책과 문서화가 필요해졌습니다.

## 2. Goals
- **UX Improvement**: 사용자가 "검토 대기 중" 상태를 명확히 인지하고, 버튼 클릭 한 번으로 승인(Approve) 및 재개(Resume)를 할 수 있는 UI를 제공한다.
- **Robustness**: Backend Checkpointer가 다중 사용자 또는 다중 세션 환경에서도 안전하게 동작하도록 `rag-{uuid}` 네임스페이스 전략을 사용하고 이를 문서화한다.
- **Documentation**: HITL 흐름과 상태 관리에 대한 아키텍처 문서를 작성한다.

## 3. Key Features
### 3.1 Resume/Approve UI
- 채팅 창 하단에 "이 답변을 승인하시겠습니까?" 와 같은 명시적 Action Button 제공.
- 승인 시 `update_state` 호출 후 `resume_workflow` API 트리거.

### 3.2 Waiting State Indicator
- 답변 생성 후 Human Interrupt 발생 시, Spinner가 멈추고 "사용자 승인 대기 중" 상태 메시지 표시.

### 3.3 Architecture Documentation
- `docs/architecture/hitl_and_persistence.md`: 상태 지속성 및 체크포인터 전략 상세 기술.

## 4. Non-Functional Requirements
- 기존 채팅 흐름(History)을 방해하지 않아야 함.
- 버튼 클릭 시 즉각적인 UI 피드백(Optimistic UI) 제공.
