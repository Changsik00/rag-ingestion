feat(spec-045): interactive refinement (canvas & clarification)

## 📋 Summary
HITL(Human-in-the-Loop) 사용자 경험을 **"단순 승인(Simple Approval)"**에서 **"적극적 개입(Interactive Refinement)"**으로 고도화했습니다.
모호한 질문에는 **역질문(Clarification)**을 던지고, 생성된 답변을 사용자가 **직접 수정(Canvas/Draft Editor)**하여 최종 승인할 수 있는 기능을 추가했습니다.

- **Before**: Agent의 답변을 "승인"하거나 "거절"만 가능 (수동적 검토).
- **After**:
    1. **Clarification**: 정보가 부족하면 Agent가 먼저 물어봄 (예: "URL이 없네요, 알려주시겠어요?").
    2. **Canvas**: 생성된 초안(Draft)을 사용자가 직접 편집 에디터에서 수정 후 승인 (능동적 개입).

## 🎯 Key Review Points
1. **AdminAgent Backend (`app/domain/services/admin_agent.py`)**:
    - `AdminState`에 `draft_content`, `is_clarification`, `missing_slots` 필드를 추가하여 상호작용 상태를 관리합니다.
    - **Router Node 개선**: 사용자 입력의 모호성(URL 누락 등)을 감지하여 `clarify` 인텐트로 라우팅합니다.
    - **Clarify Node 추가**: 부족한 정보를 채우기 위한 역질문을 생성합니다.

2. **API Response (`app/interfaces/api/v1/endpoints/admin/rag.py`)**:
    - Frontend가 새로운 상태를 인지할 수 있도록 `draft_content`, `is_clarification` 필드를 API 응답에 노출했습니다.

3. **Frontend UI (`app/admin/pages/4_RAG_Playground.py`)**:
    - **Clarification UI**: Agent가 역질문을 할 때 경고(Warning) 메시지로 시각적 구분을 제공합니다.
    - **Canvas (Draft Editor)**: HITL `paused` 상태일 때 `st.text_area`를 띄워 사용자가 답변을 직접 수정하고 "Confirm & Finalize" 할 수 있게 했습니다.

## 🧪 Verification
### Automated Tests
Backend 로직 검증을 위한 Unit Test가 작성되었습니다.
```bash
# Clarification Node 및 Feedback Loop 검증
uv run pytest tests/unit/test_admin_agent_clarification.py
```

### Manual Verification (Admin Playground)
Admin UI(`4_RAG_Playground`)에서 다음 시나리오를 검증할 수 있습니다.

#### Scenario A: Clarification (역질문)
1. **설정**: Sidebar의 "Enable HITL Review"는 **꺼져 있어도 됨** (Router 단계에서 동작).
2. **입력**: "이거 요약해줘" (URL 없이 모호하게 입력).
3. **확인**:
    - Agent가 "어떤 URL을 수집하거나 요약할까요?"라고 역질문함.
    - 메시지 위에 `⚠️ Clarification Needed` 경고 표시 확인.

#### Scenario B: Canvas (Draft Editing)
1. **설정**: Sidebar의 **"Enable HITL Review"** 스위치 **ON**.
2. **입력**: "일론 머스크에 대해 알려줘" (또는 구체적인 질문).
3. **상태 확인**:
    - "Thinking..." 후 **"Review Draft Response (HITL)"** 상태로 멈춤.
    - `📝 Draft Mode` 정보 박스와 함께 **텍스트 에디터**가 표시됨.
4. **동작 수행**:
    - 텍스트 에디터의 내용을 수정 (예: "일론 머스크는..." -> "테슬라 CEO 일론 머스크는...").
    - **"✅ Confirm & Finalize"** 버튼 클릭.
5. **결과 확인**:
    - 수정된 내용이 최종 답변으로 확정되어 대화창에 표시되는지 확인.

## 📦 Files Changed

### 🆕 New Files
- `tests/unit/test_admin_agent_clarification.py`: Clarification 및 Feedback Loop 로직 단위 테스트.

### 🛠 Modified Files
- `app/domain/services/admin_agent.py`: `AdminState` 확장, `clarify_node` 추가, Router 로직 개선.
- `app/interfaces/api/v1/endpoints/admin/rag.py`: API 응답 스키마 확장.
- `app/admin/pages/4_RAG_Playground.py`: Draft Editor 및 Clarification UI 구현.
- `specs/045-interactive-refinement/*`: Spec 문서 및 태스크 리스트.

## ✅ Definition of Done
- [x] Spec 045 Interactive Refinement (Clarification + Canvas) 구현 완료
- [x] Backend State/Router/Node 로직 구현 및 테스트 통과
- [x] Frontend(Streamlit) Draft Editor 및 Clarification UI 연동 완료
- [x] Unit Test (`tests/unit/test_admin_agent_clarification.py`) 통과
- [x] Linting (`ruff check`) 통과
