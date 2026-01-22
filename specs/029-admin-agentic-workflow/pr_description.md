# feat(spec-029): admin agentic workflow implementation

## 📋 Summary
Admin Dashboard(`RAG_Playground`)를 단순 Chain에서 **LangGraph 기반 Agent**로 업그레이드했습니다. 이제 챗봇이 사용자의 발화 의도(URL 수집 vs 지식 검색)를 파악하여 적절한 도구(`Ingest` or `Search`)를 스스로 선택하고 실행합니다.

## 🎯 Key Review Points
1.  **AdminAgent 구조**: `app/admin/agents/admin_agent.py`에서 정의된 `StateGraph` 흐름(Router -> Tools)이 적절한지.
2.  **UI UX**: `4_RAG_Playground.py`에서 `st.status`를 활용하여 에이전트의 사고 과정(Intent Detection -> Tool Execution)을 시각화한 방식.
3.  **의존성 주입**: `app/admin/pages/4_RAG_Playground.py`에서 `IngestionService`와 `Neo4jJobRepository` 등을 수동으로 조립한 부분 (FastAPI DI 재사용 제약 때문).

## 🧪 Verification
### Automated Tests
```bash
# Router Logic Unit Test
uv run pytest tests/unit/admin/test_admin_router.py
```

### Manual Verification
1.  **스크립트 검증**:
    ```bash
    uv run python scripts/verify_admin_agent.py
    ```
    - URL 수집(`ingest`) 및 검색(`search`) 시나리오 통과 확인.

2.  **UI 검증**:
    - `uv run streamlit run app/admin/pages/4_RAG_Playground.py`
    - 채팅창에 `https://example.com 읽어줘` 입력 시 수집 동작 확인.
    - 일반 질문 시 RAG 답변 동작 확인.

## 📦 Files Changed
### 🆕 New Files
- `app/admin/agents/__init__.py`
- `app/admin/agents/admin_agent.py`: LangGraph 에이전트 핵심 로직
- `tests/unit/admin/test_admin_router.py`: 라우터 단위 테스트
- `scripts/verify_admin_agent.py`: E2E 검증 스크립트

### 🛠 Modified Files
- `app/admin/pages/4_RAG_Playground.py`: AdminAgent 연동 및 UI 업데이트
- `backlog/queue.md`: Spec 029 완료 처리

## ✅ Definition of Done
- [x] LangGraph 도입 및 Router/Tool 노드 구현
- [x] Streamlit UI에서 Agent 실행 흐름 시각화
- [x] URL 수집 및 검색 기능 정상 동작 검증
- [x] 단위 테스트 통과
