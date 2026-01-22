# Spec-028: Agentic MCP Server (Active Ingestion)

## 📋 배경 및 문제 정의 (Background & Problem)
현재 시스템은 관리자 패널(Streamlit)이나 Swagger API를 통해서만 데이터를 수집(Ingest)할 수 있어, 외부 LLM(Claude Desktop, Cursor 등)과 대화하는 도중에 즉각적으로 새로운 URL을 학습시키거나 저장된 지식을 조회하기 어렵습니다.
사용자가 채팅창에서 "이 링크 읽어줘"라고 말했을 때 바로 수행할 수 있도록, **MCP(Model Context Protocol)** 표준을 따르는 서버를 구축하여 우리 시스템을 LLM의 "도구(Tool)"로 노출해야 합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **MCP Server 구축**: `mcp` 라이브러리를 사용하여 표준 프로토콜을 지원하는 서버 구현.
2. **`ingest_url` Tool 제공**:
    - URL을 입력받아 RAG 파이프라인에 수집 요청.
    - 수집 작업이 완료될 때까지 대기하거나(Synchronous), Job Status를 반환해야 함 (초기 버전은 Sync 권장).
3. **`search_knowledge_base` Tool 제공**:
    - 질의(Query)를 받아 RAG 검색 수행.
    - 검색된 지식을 LLM이 이해하기 쉬운 포맷으로 반환.

### Non-Functional Requirements
1. **Easy Integration**: 별도의 복잡한 설정 없이 `uv run mcp-server` 등 간단한 명령어로 실행 가능해야 함.
2. **Response Time**: Ingestion은 시간이 걸릴 수 있으므로, 타임아웃 처리가 중요함.

## ✅ Definition of Done
1. `uv run mcp-server` 명령으로 서버가 정상 구동되어야 함.
2. `mcp-inspector` 또는 실제 Claude Desktop에서 `ingest_url` 도구를 호출하여 DB에 데이터가 쌓이는 것을 확인.
3. `search_knowledge_base` 도구를 통해 방금 넣은 데이터가 검색되는지 확인.
4. 단위 테스트(`test_mcp_server.py`) 통과.
