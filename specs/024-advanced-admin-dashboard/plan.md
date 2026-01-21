# Implementation Plan: Spec-024

## 📋 Branch Strategy
- `feature/spec-024-admin-dashboard`

## 🛑 User Review Required
- [ ] `streamlit`, `streamlit-agraph`, `plotly` 의존성 추가 필요. (현재 `pyproject.toml`에 없음)

## 🎯 Core Strategy
- **Service-First TDD**: UI(Streamlit)는 테스트가 어려우므로, 모든 로직(Graph Fetching, Status Parsing, Feedback)을 `app/admin/services/`에 격리하고 **Unit Test**로 검증한 뒤 UI에 연결한다.
- **Streamlit**: 빠른 UI 프로토타이핑 및 데이터 시각화.
- **Components**:
    - `streamlit-agraph`: Graph Visualization.
    - `plotly`: Reasoning Trace Visualization.
- **User-Friendly**: 노코드(No-Code) 쿼리 빌더 및 직관적인 상태 표시.

## 📂 Proposed Changes

### [Dependency Management]
#### [MODIFY] `pyproject.toml`
- Add `streamlit>=1.30.0`
- Add `streamlit-agraph>=0.0.45`
- Add `plotly>=5.18.0`

### [Admin Application]
#### [NEW] `app/admin/dashboard.py`
- Main Entry Point.
- 전역 설정 및 사이드바 Navigation.

#### [NEW] `app/admin/pages/1_Graph_Explorer.py`
- **Presets**: "사람-사람 관계", "특정 기술 관련 문서" 등 원클릭 쿼리 버튼.
- **Builder**: Dropdown(Entity Type, Relation) 선택으로 Cypher 자동 생성.
- Graph Visualization.

#### [NEW] `app/admin/pages/2_HITL_Control.py`
- Thread List & **Current Status Badge** ("Thinking", "Idle").
- State Inspection & Resume Action.

#### [NEW] `app/admin/pages/3_Trace_Viewer.py`
- Job ID 입력 -> Execution Trace Visualization.
- Failure Analysis 결과 표시.

#### [NEW] `app/admin/pages/4_RAG_Playground.py`
- Chat Interface.
- Retrieved Context 표시.
- **Feedback UI**: Thumbs up/down 버튼 및 로그 저장.

## 🧪 Verification Plan

### Automated Tests
- UI 테스트는 제외(Manual Verification에 의존).
- Backend Service Logic에 대한 Unit Test 작성.

### Manual Verification
1. **Setup**: `uv sync` 후 `streamlit run app/admin/dashboard.py` 실행.
2. **Graph**: 데이터 수집 후 Graph Explorer에서 노드 생성 확인.
3. **HITL**: `construct_extraction_prompt`에서 강제 에러 유발 -> HITL Control에서 Resume -> 정상 완료 확인.
4. **Trace**: 실패한 Job ID 입력 -> Trace Viewer에서 로그 확인.
