# Implementation Plan - Spec 058: API Input Validation & Error Handling

## 개요
이 계획은 API의 입력 유효성 검사를 강화하고 에러 응답 형식을 표준화하기 위한 구체적인 변경 사항을 담고 있습니다.

## Proposed Changes

### [API DTO & Validation]

#### [MODIFY] [ingest.py](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/v1/dto/ingest.py)
- `ChunkingConfigDTO` 추가 (Domain의 `ChunkingConfig` 속성들과 매핑).
- `IngestRequest`의 `chunking_config` 타입을 `ChunkingConfigDTO | None`으로 변경하여 타입 세이프티 확보.

#### [MODIFY] [rag.py](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/v1/dto/rag.py)
- `AdvancedSettings`의 제약 조건 강화 (예: `ge`, `le` 적절성 검토).
- `ChatRequest`의 `filters` 필드에 대한 추가적인 검증 로직 고려.

---

### [Error Handling]

#### [MODIFY] [error_handlers.py](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/error_handlers.py)
- `from fastapi.exceptions import RequestValidationError` 추가.
- `RequestValidationError` 핸들러 구현: Pydantic 에러 메시지를 추출하여 `ErrorResponse` 형식의 `details` 필드에 담아 반환.
- `HTTPException` 핸들러 추가: FastAPI 내부 HTTPException(예: 405 Method Not Allowed)도 표준 형식으로 반환하도록 처리.

---

### [Testing]

#### [NEW] [test_api_validation.py](file:///Users/ck/Project/doit/rag-ingestion/tests/integration/functional/test_api_validation.py)
- 유효하지 않은 URL 요청 테스트 (422)
- 범위를 벗어난 `top_k`, `temperature` 요청 테스트 (422)
- 잘못된 `chunking_config` 구조 요청 테스트 (422)
- 위 케이스들이 표준 `ErrorResponse` 형식을 준수하는지 검증.

## Verification Plan

### Automated Tests
*   **API Validation Test**: 신규 생성한 테스트 파일 실행
    ```bash
    uv run pytest tests/integration/functional/test_api_validation.py
    ```
*   **Existing Functional Tests**: 기존 기능 영향도 파악을 위해 전체 테스트 실행
    ```bash
    uv run pytest tests/integration/functional/test_api_endpoints.py
    ```

### Manual Verification
*   Swagger UI (`/docs`) 접속 후 `POST /v1/ingest/web` 혹은 `POST /v1/rag/ask` 엔드포인트에 고의로 잘못된 데이터를 전송하여 브라우저에서 반환되는 JSON 형식을 확인합니다.
