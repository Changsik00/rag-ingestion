# feat(spec-028): agentic mcp server implementation

## 📋 Summary
외부 LLM(Claude, Cursor 등)이 프로젝트의 RAG 파이프라인을 도구(Tool)로 처럼 사용할 수 있도록 **Agentic MCP Server**를 구현했습니다. 이를 통해 채팅 인터페이스에서 실시간으로 URL을 학습시키거나 저장된 지식을 지능형 검색(Hybrid Search)으로 조회할 수 있습니다.

## 🎯 Key Review Points
1. **MCP 프로토콜 준수**: `fastmcp`를 사용하여 수집(`ingest_url`)과 검색(`search_knowledge_base`) 도구가 표준에 맞게 구현되었는지.
2. **동기 처리(Blocking Ingestion)**: `ingest_url`이 현재 동기 방식(`create_job` -> `process_job`)으로 구현되어 있습니다. 대용량 페이지 수집 시 타임아웃 가능성에 대한 검토가 필요합니다.
3. **수동 의존성 주입**: FastAPI 컨테이너 외부에서 실행되므로 `provide_ingestion_service` 등을 통해 수동으로 의존성을 연결한 로직이 적절한지.

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests (Mocking Service Layer)
uv run pytest tests/unit/interfaces/test_mcp_server.py
```

### Manual Verification
1. `uv run python app/interfaces/mcp/server.py` 실행 (FastMCP CLI).
2. `mcp-inspector`를 통해 로컬 서버 연결 후 Tool 호출 테스트.

## 📦 Files Changed

### 🆕 New Files
- `app/interfaces/mcp/server.py`: MCP 서버 엔트리포인트 및 도구 구현
- `app/interfaces/mcp/__init__.py`: 패키지 초기화
- `tests/unit/interfaces/test_mcp_server.py`: MCP 도구 및 서비스 연동 단위 테스트

### 🛠 Modified Files
- `pyproject.toml`: `mcp` 패키지 의존성 추가

**Total:** 4 files changed


## ✅ Definition of Done
- [x] `uv run`으로 MCP 서버 실행 가능 확인
- [x] `ingest_url` 도구가 IngestionService를 정상 호출하고 결과 반환 확인
- [x] `search_knowledge_base` 도구가 RAGService를 정상 호출하고 결과 반환 확인
- [x] 단위 테스트 통과 (2 passed)
