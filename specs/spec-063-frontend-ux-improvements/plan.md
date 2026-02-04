# Plan: Spec 063 Admin UI/UX Improvements

## [Goal Description]
Admin Dashboard의 사용성(UX)을 개선하고, RAG 품질 검증을 위한 도구를 통합합니다.
1.  **Verification Lab**: CLI 스크립트(`manual_rag_verification.py`)를 Admin UI로 이식하여 접근성 향상.
2.  **Graph Explorer UX**: Dark Mode 가시성 확보 및 프리셋 로딩 버그 수정.
3.  **User Feedback**: Chat UI의 피드백 버튼 동작 확인 및 연동.

## User Review Required
> [!NOTE]
> Graph Explorer의 Node Color 변경은 기존 사용자 경험에 변화를 줄 수 있습니다. (기존 파스텔 톤 -> High Contrast 필요 시 변경)

## Proposed Changes

### Admin Dashboard (Presentation Layer)
#### [NEW] [5_Verification_Lab.py](file:///Users/ck/Project/doit/rag-ingestion/admin/pages/5_Verification_Lab.py)
- `scripts/manual_rag_verification.py` 로직 이식.
- `st.form`을 사용하여 질문 입력 및 실행 제어.
- `app.interfaces.api.dependencies.get_rag_service` 활용하여 Service 바로 호출 (Admin App Instance가 App Context 공유 가정).

#### [MODIFY] [1_Graph_Explorer.py](file:///Users/ck/Project/doit/rag-ingestion/admin/pages/1_Graph_Explorer.py)
- **Preset Fix**: `st.text_area`에 `key="cypher_input"` 추가 및 `st.button` 콜백에서 `st.session_state["cypher_input"]` 업데이트.
- **Style**: `agraph` Config 및 Node Color 로직 수정. `Dynamic Theme` 적용 또는 Dark/Light 모두 잘 보이는 Color Palette(가독성 중심) 적용.

#### [MODIFY] [4_RAG_Playground.py](file:///Users/ck/Project/doit/rag-ingestion/admin/pages/4_RAG_Playground.py)
- Feedback API 호출부 Error Handling 강화 (Toast 메시지 등).

## Verification Plan

### Automated Tests
- UI 변경 사항이므로 Automated Test보다는 Manual Verification 위주.
- 기존 Backend API 테스트는 `rag.py` 변경이 없으므로 Regression Test (`test_rag_session_cleanup.py` 등) 수행.

### Manual Verification
1.  **Verification Lab**:
    - Admin 접속 -> `Verification Lab` 메뉴 진입.
    - 질문 입력 -> `Run` 클릭 -> Answer 및 Source 출력 확인.
2.  **Graph Explorer**:
    - Dark Mode 설정 (OS/Browser).
    - Node Label 및 Edge 연결선이 배경과 분리되어 잘 보이는지 확인.
    - `Preset` 선택 -> `Load` 클릭 -> Query Text Area 내용 변경 확인 -> `Run` 실행 확인.
3.  **Feedback**:
    - `RAG Playground` -> 질문 -> 답변 생성.
    - `Good` 버튼 클릭 -> "Thanks for your feedback" Toast 확인.
    - Backend Log 또는 DB에 Feedback 저장 여부 확인 (Optional).
