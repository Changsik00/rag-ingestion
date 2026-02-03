# Spec 058: API Input Validation & Error Handling

## 1. 개요 (Overview)
본 스펙은 RAG Ingestion API의 견고함을 높이기 위해 입력 데이터 검증(Input Validation)을 강화하고, 시스템 전반의 예외 처리(Error Handling)를 표준화하는 것을 목표로 합니다. 클라이언트/프론트엔드 개발자가 API 에러를 명확하게 이해하고 처리할 수 있도록 머신 리더블(Machine-readable)한 에러 코드를 제공합니다.

## 2. 목표 (Goals)
*   **입력 검증 강화**: Pydantic을 활용하여 모든 API 엔드포인트의 요청 데이터 검증 로직을 고도화합니다.
*   **에러 응답 표준화**: FastAPI의 기본 422 (Unprocessable Entity) 에러를 포함한 모든 에러 응답을 프로젝트의 `ErrorResponse` 규격으로 통일합니다.
*   **상세 예외 처리**: 도메인/인프라 레이어의 예외를 적절한 HTTP 상태 코드 및 비즈니스 에러 코드로 매핑합니다.
*   **테스트 커버리지**: 유효하지 않은 입력 값에 대한 실패 케이스 테스트를 추가합니다.

## 3. 상세 설계 (Technical Design)

### 3.1 입력 검증 고도화 (DTO Enhancements)
*   **IngestRequest**: `chunking_config` 필드를 단순 `dict`에서 `ChunkingConfigDTO` (또는 기존 Value Object 연동)로 구체화하여 파라미터 유효성 검증.
*   **ChatRequest**: `message` 외에 `filters` 등의 필드에 대한 스키마 정의 강화.
*   **Constraint 추가**: `min_length`, `ge`, `le`, `pattern` 등을 적극적으로 활용하여 LLM이나 DB에 전달되기 전에 필터링.

### 3.2 에러 핸들링 아키텍처 (Error Handling)
*   **Global Exception Handlers**: `app/interfaces/api/error_handlers.py`에 다음 핸들러 추가/수정:
    *   `RequestValidationError`: FastAPI 기본 핸들러를 오버라이드하여 `ErrorResponse` 형식으로 반환.
    *   `HTTPException`: Starlette의 기본 예외 처리 커스터마이징.
*   **Error Codes**: 
    *   `VALIDATION_ERROR`: 입력 값 유효성 검증 실패 (422)
    *   `INVALID_PARAMETER`: 잘못된 파라미터 조합 (400)
    *   `UPSTREAM_ERROR`: 외부 서비스(LLM, Scraper) 연동 실패 (502)

### 3.3 표준 응답 규격 (Review)
`app/interfaces/api/v1/dto/common.py`의 `ErrorResponse`를 적극 활용:
```json
{
  "status": "error",
  "message": "상세 에러 메시지",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "error reason"
  }
}
```

## 4. 기대 효과 (Expected Impact)
*   클라이언트 앱(Streamlit 등)과의 통신 시 예측 가능한 에러 처리 가능.
*   서버 내부 로직에 잘못된 데이터가 유입되는 것을 원천 차단하여 시스템 안정성 향상.
*   디버깅 효율성 증대.

## 5. 제외 범위 (Non-Goals)
*   인증/권한(Auth) 관련 에러 처리 (추후 별도 Spec 진행 가능).
*   로깅 인프라의 근본적인 변경.
