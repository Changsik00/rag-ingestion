# Implementation Plan: Spec-028

## 📋 Branch Strategy
- `feature/spec-028-mcp-server`

## 🛑 User Review Required
- [x] **동기 처리(Sync) 방식**: Ingestion은 수 초~수십 초가 걸릴 수 있습니다. 초기 버전에서는 LLM이 결과를 기다릴 수 있도록 `sync` 방식으로 구현하고 타임아웃을 넉넉히 잡을 예정입니다. 괜찮으신가요?

## 🎯 Core Strategy
- **FastMCP 사용**: `mcp` 라이브러리의 고수준 API인 `FastMCP`를 사용하여 빠르고 표준화된 방식으로 서버를 구현합니다.
- **기존 Service 재사용**: `app/domain/services` 내의 로직을 그대로 재사용하여 중복을 방지합니다.

## 📂 Proposed Changes

### [Interface Layer]

#### [NEW] `app/interfaces/mcp_server.py`
MCP 서버 엔트리포인트 및 도구 정의 파일입니다.
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RAG Agent")

@mcp.tool()
async def ingest_url(url: str) -> str:
    # IngestionService 호출
    pass

@mcp.tool()
async def search_knowledge_base(query: str) -> str:
    # RAGService 호출
    pass
```

### [Configuration]

#### [MODIFY] `pyproject.toml`
`mcp` 의존성을 추가합니다.

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests
uv run pytest tests/unit/interfaces/test_mcp_server.py
```

### Manual Verification
1. `uv run mcp-inspector app/interfaces/mcp_server.py` 실행.
2. Inspector UI에서 `ingest_url` 도구에 테스트 URL 입력 및 실행.
3. 로그 확인 및 DB 저장 확인.
