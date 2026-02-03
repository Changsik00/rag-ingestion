# feat(spec-058): api input validation and error handling

## Summary
이 PR은 RAG Ingestion API의 입력 값 검증을 강화하고, 시스템 전반의 에러 응답 포맷을 표준화하여 API의 견고성과 예측 가능성을 향상시킵니다.

## Type of Change
- [x] New Feature (새로운 기능 추가)
- [ ] Bug Fix (버그 수정)
- [x] Refacotr (리팩토링)
- [ ] Documentation (문서 업데이트)

## Key Changes

### 1. DTO Validation 강화 (`app/interfaces/api/v1/dto/ingest.py`)
- **`ChunkingConfigDTO` 추가**: 청킹 전략(`recursive`, `semantic`) 및 관련 파라미터(`chunk_size`, `chunk_overlap`)에 대한 Pydantic 모델을 정의하여 유효성 검증을 수행합니다.
- `IngestRequest.chunking_config` 필드에 해당 DTO를 적용하여 잘못된 설정 값이 유입되는 것을 방지합니다.

### 2. Global Error Handling 표준화 (`app/interfaces/api/error_handlers.py`)
- **`RequestValidationError` 핸들러**: 입력 값 검증 실패 시 발생하는 422 에러를 프로젝트 표준 `ErrorResponse` 포맷으로 변환하며, 상세 필드 오류 정보를 제공합니다.
- **`HTTPException` 핸들러**: 404, 405 등 일반적인 HTTP 에러도 표준 JSON 응답으로 통일했습니다.

## Verification
- **New Integration Tests**: `tests/integration/functional/test_api_validation.py`를 추가하여 유효하지 않은 입력(URL, Settings) 및 에러 포맷을 검증했습니다.
- **Regression Tests**: 기존 `test_api_endpoints.py`를 통과하여 기존 기능에 영향이 없음을 확인했습니다.

```bash
uv run pytest tests/integration/functional/test_api_validation.py
```
