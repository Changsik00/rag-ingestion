# Implementation Plan: Spec-045

## 📋 Branch Strategy
- `feature/045-interactive-refinement`

## 🛑 User Review Required
- **UI Limitation**: Streamlit은 Real-time Collaboration(동시 편집)을 지원하지 않으므로, `st.text_area`를 활용한 "Draft Mode & Submit" 방식으로 구현됩니다.
- **Interrupt Strategy**: `human_review` 노드 외에 `clarify_intent` 노드에서도 사용자의 입력을 기다리기 위해 그래픽 실행이 중단(Interrupt)됩니다.

## 📂 Proposed Changes

### [Backend] `app/domain/services/`
#### [MODIFY] `app/domain/services/admin_agent.py`
1.  **State Schema Update (`AdminState`)**
    - `draft_content: str | None`: 생성된 초안 내용 저장.
    - `is_clarification: bool`: 역질문 상태 플래그.
    - `missing_slots: list[str]`: 누락된 필수 정보 (URL, 기간 등).

2.  **Workflow Update (`build_workflow`)**
    - **Nodes**: `clarify_node` 추가.
    - **Edges**:
        - `router` -> `clarify` (Condition: Intent 불명확 또는 슬롯 누락).
        - `clarify` -> `END` (Human Feedback 대기).
        - `router` -> `draft_gen` (Condition: 요약/작문 요청) -> `human_review` (Draft 확인).

3.  **Ambiguity Detection Logic (`router_node`)**
    - LLM Prompt에 "Missing Information Detection" 추가.
    - 필수 파라미터가 없으면 `intent="clarify"` 반환.

### [Frontend] `admin/pages/`
#### [MODIFY] `admin/pages/4_RAG_Playground.py`
1.  **Draft Editor (Canvas Mode)**
    - 검사 조건: `state["step"] == "human_review"` (or equivalent status) AND `state.get("draft_content")`.
    - UI Component:
        ```python
        with st.form("draft_form"):
            edited_content = st.text_area("📝 Edit Draft", value=draft_content, height=400)
            if st.form_submit_button("✅ Confirm & Finalize"):
                # Resume with edited content
                resume_workflow(input={"action": "approve", "content": edited_content})
        ```

2.  **Clarification UI**
    - 검사 조건: `state.get("is_clarification")` is True.
    - UI Style: `st.warning("⚠️ " + clarification_question)` 또는 Chat Message 내 Highlight 적용.

### [Domain] `app/domain/services/`
#### [MODIFY] `app/domain/services/intent_classifier.py`
- (Optional) `Intent` Enum에 `CLARIFICATION_NEEDED` 추가 또는 `Router` 로직 내 통합.

## 🧪 Verification Plan

### 1. Verification Script (`scripts/verify_interactive.py`)
> 실제 LLM 호출 없이 State Transition을 검증합니다.

- **Scenario 1: Ambiguity & Clarification**
    - Input: "요약해줘" (Context 없음)
    - Expect: Router -> `clarify_node` -> Interrupt.
    - Check: State에 `is_clarification=True` 확인.
    - Resume: "https://example.com 뉴스 요약해줘"
    - Expect: `clarify_node` -> `router` -> `ingest` or `search` -> Success.

- **Scenario 2: Draft Editing**
    - Input: "이 내용으로 보고서 초안 써줘"
    - Expect: `search` -> `draft_gen` -> Interrupt (Human Review).
    - Check: State에 `draft_content` 존재 확인.
    - Resume: `{"action": "approve", "content": "Modified Content"}`
    - Expect: Final Answer에 "Modified Content" 반영 확인.

### 2. Manual Verification (RAG Playground)
1.  **Clarification Test**:
    - "분석해줘" 입력 -> "어떤 문서를 분석할까요?" 역질문 확인.
    - 문서 ID/URL 입력 후 정상 진행 확인.
2.  **Canvas Test**:
    - "A 문서 기반으로 블로그 글 초안 작성해줘" 입력.
    - Draft Editor 표시 확인 -> 내용 수정(오타 수정 등).
    - "Confirm" 클릭 -> 최종 말풍선에 수정된 내용이 표시되는지 확인.
