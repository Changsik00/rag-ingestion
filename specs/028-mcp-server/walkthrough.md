# Walkthrough: Spec-028 (Agentic MCP Server)

## 1. 개요
*   **목표**: 외부 LLM(Claude 등)이 능동적으로 URL을 수집하고 지식을 검색할 수 있도록 MCP(Model Context Protocol) 서버를 구축했습니다.
*   **주요 변경 사항**:
    *   `mcp` 패키지 추가.
    *   `app/interfaces/mcp/server.py` 구현 (`ingest_url`, `search_knowledge_base` 도구 제공).
    *   기존 IngestionService 및 RAGService와 연동.

## 2. 구현 상세
### 2.1 MCP Server (`server.py`)
*   `FastMCP`를 사용하여 표준 호환 서버 구현.
*   `provide_ingestion_service`, `provide_rag_service` 헬퍼 함수를 통해 의존성 수동 주입(FastAPI 의존성 제거).

### 2.2 Tools
1.  **ingest_url**:
    *   `IngestionService.create_job` -> `process_job` (Blocking) 순차 실행.
    *   수집 완료 후 상태 및 메타데이터 반환.
2.  **search_knowledge_base**:
    *   `RAGService.search` (Hybrid Retrieval) 결과 반환.
    *   LLM이 이해하기 쉬운 텍스트 포맷으로 변환.

## 3. 테스트 및 검증
### 3.1 단위 테스트 (Unit Test)
*   **파일**: `tests/unit/interfaces/test_mcp_server.py`
*   **내용**: Service Mocking을 통해 Tool 호출 및 파라미터 전달, 반환값 포맷팅 검증.
*   **결과**: Passed (2 tests)

### 3.2 수동 검증 (Manual Verification)
*   **스크립트**: `scripts/verify_mcp_agent.py`
    *   `GEMINI_API_KEY` 환경변수를 사용하여 Google GenAI 모델과 연동.
    *   **시나리오**: "Rules: You MUST use the 'agent_ingest_url' tool..." 프롬프트로 강제 호출.
*   **결과**:
    ```text
    User: Rules: You MUST use the 'agent_ingest_url' tool... targets https://news.ycombinator.com
    ...
    Tool Output: Successfully ingested: https://news.ycombinator.com
    Status: JobStatus.COMPLETED
    ```
*   **수정 사항**:
    *   `ChromaStorage`: Metadata에 `None` 값이 있을 경우 저장 실패하는 문제 수정 (`None` 필터링).
    *   `MCP Server`: `IngestionJob` 객체에 존재하지 않는 `metadata` 속성 접근 제거.
    *   `IngestionJob`: `id` 대신 `job_id` 필드명 사용하도록 수정.
