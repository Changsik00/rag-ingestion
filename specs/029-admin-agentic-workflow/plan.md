# Implementation Plan: Spec-029

## 📋 Branch Strategy
- `feature/spec-029-admin-agentic`

## 🛑 User Review Required
- [x] **UI 변경**: 기존의 즉각적인 응답 방식에서, 도구 실행 과정을 보여주는 `st.status` 또는 `st.expander` 기반의 UI로 변경됩니다.

## 🎯 Core Strategy
1.  **LangGraph 도입**: `AdminAgent`를 LangGraph `StateGraph`로 구현하여 확장성 및 상태 관리 능력 확보.
2.  **Router Node**: LLM을 사용하여 사용자 의도를 `ingest` 또는 `search`로 분류.
3.  **Tool Nodes**: Spec 028의 기능과 유사하게 `IngestionService`와 `RAGService`를 래핑한 노드 구현.
4.  **Backend-for-Frontend (BFF)**: Streamlit UI에 특화된 Agent 로직을 `app/admin/agents/` 디렉토리에 분리.

## 📂 Proposed Changes

### `app/admin/agents/` [NEW]

#### [NEW] `app/admin/agents/admin_agent.py`
```python
# LangGraph definition
class AdminState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    
def router_node(state: AdminState) -> AdminState:
    # LLM Intent Classification
    ...

def ingest_node(state: AdminState) -> AdminState:
    # Call IngestionService
    ...
    
def search_node(state: AdminState) -> AdminState:
    # Call RAGService
    ...

def build_admin_agent():
    workflow = StateGraph(AdminState)
    ...
    return workflow.compile()
```

#### [NEW] `app/admin/agents/__init__.py`

### `app/admin/pages/` [MODIFY]

#### [MODIFY] `app/admin/pages/4_RAG_Playground.py`
- 기존 `rag_service.retrieve_and_generate` 직접 호출 제거.
- `AdminAgent` 초기화 및 `agent.ainvoke` 호출.
- `st.status`를 활용한 단계별 실행 과정 시각화.

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (Router Logic)
uv run pytest tests/unit/admin/test_admin_router.py
```

### Manual Verification
1.  **URL 수집**: 채팅창에 `https://example.com` 입력 -> "Ingesting..." 표시 및 완료 메시지 확인.
2.  **질문 검색**: "RAG가 뭐야?" 입력 -> "Searching..." 표시 및 답변 확인.
3.  **복합 의도 확인**: "이 링크 읽고 요약해줘: https://..." -> 수집 후 요약(답변)까지 이어지는지 확인 (Router가 Sequential하게 동작 가능한지 확인).
