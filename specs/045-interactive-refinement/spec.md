# Spec 045: Interactive Refinement (Canvas & Clarification)

## 🎯 Goal
- **Clarification**: Agent가 사용자의 의도가 모호하다고 판단할 경우, 즉시 답변하지 않고 **역질문(Clarification Question)**을 통해 정보를 보완합니다.
- **Canvas (Draft Editing)**: 긴 형태의 콘텐츠(요약, 보고서) 생성 시, 사용자가 **초안(Draft)을 직접 수정**하고 승인할 수 있는 UI/UX를 제공합니다.

## 📜 Context
- 현재 HITL은 답변 생성 "후"에 승인/반려(Confirm/Reject)만 가능함.
- "요약해줘" 같은 모호한 요청 시, Agent가 임의로 판단하거나 실패하는 경우가 많음.
- 사용자는 생성된 텍스트를 "조금만 고쳐서" 쓰고 싶은데, 다시 프롬프트로 지시해야 하는 번거로움이 있음.

## 🏗️ Proposed Changes

### 1. Clarification Logic (Adaptive Routing)
- **Component**: `AdminAgent` (Graph)
- **Logic**:
    - `IntentClassifier`가 불확실하거나, 필수 파라미터(URL 등)가 누락되었을 때 `clarify_node`로 진입.
    - **Draft State**: `clarification_needed` 플래그 활성화.
    - **Response**: "어떤 문서를 요약할까요?" 등의 질문 반환.

### 2. Canvas UI (Frontend)
- **Component**: `4_RAG_Playground.py`
- **UI UX**:
    - Agent의 응답 상태가 `draft` 또는 `needs_refinement`일 때, 대화창 하단에 **전용 편집 영역(Text Area / Canvas)** 표시.
    - 사용자가 텍스트를 직접 수정한 후 `Confirm` 버튼을 누르면, 수정된 내용이 시스템에 반영되거나 최종 답변으로 확정됨.

### 3. State Management
- **State Schema**: `AdminState`에 `draft_content`, `is_draft` 필드 추가.
- **Persistence**: 기존 `checkpoints.sqlite`를 통해 대화 턴 간 상태 유지.

## 🧪 Verification Plan

### Automated Verification
- `scripts/verify_interactive.py`:
    - **Ambiguity Test**: "요약해줘" 입력 -> Agent가 역질문하는지 확인.
    - **Draft Test**: 임의의 Draft 상태 주입 -> 사용자 수정(Simulated) -> Finalize 확인.

### Manual Verification
- **Scenario 1 (Clarification)**:
    1. Playground에서 "이거 읽어줘" 입력.
    2. Agent가 "URL을 입력해주세요"라고 되묻는지 확인.
    3. URL 입력 후 진행 확인.
- **Scenario 2 (Canvas)**:
    1. "A 문서 요약해줘" -> Agent가 초안 생성.
    2. Draft UI에서 내용 일부 수정.
    3. "Confirm" 클릭 -> 최종 답변에 수정본이 남는지 확인.
