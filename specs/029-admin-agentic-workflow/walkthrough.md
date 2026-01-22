# Walkthrough: Spec-029 Admin Agentic Workflow

## 📋 개요
이 문서는 **Spec-029: Admin Agentic Workflow**의 구현 및 검증 과정을 기록합니다.
Admin Dashboard(`4_RAG_Playground.py`)에 LangGraph 기반의 `AdminAgent`를 도입하여, 사용자의 URL 수집 요청과 지식 검색 요청을 지능적으로 구분하고 실행하는 기능을 구현했습니다.

## 🛠 구현 내용
### 1. `AdminAgent` 구현 (`app/admin/agents/admin_agent.py`)
- **State**: `AdminState` (messages, intent, tool_output, context_data)
- **Router**: LLM을 사용하여 사용자 입력에서 URL 감지 시 `ingest`, 그 외에는 `search`로 Intent 분류.
- **Tools**:
    - `ingest_node`: `IngestionService`를 호출하여 비동기 수집 작업 생성 및 실행 대기.
    - `search_node`: `RAGService`를 호출하여 답변 및 Context 생성.
- **Graph**: `Router` -> `Ingest` / `Search` -> `END` 흐름 구성.

### 2. Admin UI 연동 (`4_RAG_Playground.py`)
- 기존의 직접 서비스 호출 방식을 제거하고 `AdminAgent` 워크플로우 실행으로 대체.
- `st.status`를 사용하여 "Thinking...", "Detecting intent...", "Ingestion Completed" 등 진행 상황 시각화.
- `context_data`를 통해 검색된 지식(Graph Fact, Vector Chunks)을 UI에 표시.

## 🧪 검증 결과
### 1. Automated Unit Tests
- `tests/unit/admin/test_admin_router.py`: Router의 Intent 분류(URL vs 일반 질문) 로직 검증 완료.

### 2. Manual Verification Script (`scripts/verify_admin_agent.py`)
- **Scenario 1 (Ingest)**: "이 링크 수집해줘: https://example.com"
    - **Result**: Intent `ingest` 감지, `IngestionService` 실행, "✅ 수집 완료" 메시지 반환 확인.
- **Scenario 2 (Search)**: "RAG가 뭐야?"
    - **Result**: Intent `search` 감지, `RAGService` 실행, 답변 및 Context 반환 확인.

### 🐛 이슈 및 해결
1.  **IngestionJob Metadata AttributeError**:
    - `IngestionJob` 엔티티에 `metadata` 속성이 없음에도 접근하려다 오류 발생.
    - 성공 메시지를 단순화(`✅ 수집 완료: {url}`)하여 해결.
2.  **ChunkerService Import Error**:
    - Protocol(`ChunkerService`)과 구현체(`LangChainChunker`) import 경로 혼동.
    - `app.infrastructure.chunker.langchain_chunker`에서 올바르게 import하여 해결.

## ✅ 결론
Admin Chat이 이제 단순 봇이 아닌 "Agent"로서 동작하며, 사용자의 요청에 따라 능동적으로 수집 도구를 사용할 수 있음을 확인했습니다.
