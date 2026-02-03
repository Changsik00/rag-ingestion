# feat(spec-058): api input validation and error handling

## 📋 Summary

### 배경 및 목적
RAG 시스템의 안정성을 위해 API 입력 단계에서 잘못된 데이터를 사전에 차단하고, 에러 발생 시 클라이언트가 명확히 인지할 수 있도록 응답 포맷을 표준화할 필요가 있습니다. 이번 변경을 통해 Pydantic 기반의 엄격한 유효성 검증과 일관된 에러 핸들링 체계를 구축했습니다.

### 주요 변경 사항
- [x] **DTO Validation 강화**: `ChunkingConfigDTO`를 도입하여 청킹 전략 및 파라미터의 유효성 검증 로직을 추가했습니다.
- [x] **IngestRequest 개선**: `dict` 타입을 구체적인 DTO로 대체하여 Type Safety를 확보했습니다.
- [x] **Global Error Handler**: `RequestValidationError` 및 `HTTPException` 발생 시 프로젝트 표준 `ErrorResponse` 포맷으로 자동 변환되도록 구현했습니다.
- [x] **Admin UI Improvement**: Streamlit Admin Client가 표준 에러 포맷을 파싱하여 가독성 좋은 에러 메시지를 표시하도록 개선했습니다.
- [x] **Validation Tests**: 잘못된 입력(URL, Settings 등)에 대한 실패 시나리오 테스트를 추가했습니다.

## 🎯 Key Review Points
1. **Error Response Standard**: 모든 에러 상황(404, 405, 422 등)에서 `status`, `error_code`, `message`, `details` 필드가 일관되게 반환되는지 확인 부탁드립니다.
2. **DTO Constraints**: `ChunkingConfigDTO`의 제약 조건(예: `chunk_overlap < chunk_size`)이 적절한지 검토가 필요합니다.
3. **Backward Compatibility**: 기존 엔드포인트 호출 규약이 깨지지 않았는지(회귀 테스트 통과 여부) 확인했습니다.

## 🧪 Verification

### Automated Tests
```bash
# New Validation Tests
uv run pytest tests/integration/functional/test_api_validation.py

# Regression Tests (Existing Endpoints)
uv run pytest tests/integration/functional/test_api_endpoints.py
```

### Manual Verification
Swagger UI (`/docs`)를 통해 고의로 잘못된 페이로드를 전송하여 422 에러 응답이 표준 포맷으로 오는지 확인했습니다.

## 📦 Files Changed

### 🆕 New Files
- `tests/integration/functional/test_api_validation.py`: API 유효성 검증 시나리오 테스트

### 🛠 Modified Files
- `app/interfaces/api/v1/dto/ingest.py`: `ChunkingConfigDTO` 추가 및 `IngestRequest` 수정
- `app/interfaces/api/error_handlers.py`: `RequestValidationError`, `HTTPException` 핸들러 추가
- `admin/utils/api_client.py`: 에러 응답 파싱 및 출력 로직 개선
- `specs/058-api-input-validation-error-handling/`: 관련 문서 일체

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `spec.md`, `plan.md`, `task.md` 작성 및 최신화
- [x] `walkthrough.md` 작성 완료
- [x] Pydantic 기반 DTO 적용 및 Global Error Handler 구현 완료
