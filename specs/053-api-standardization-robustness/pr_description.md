# feat(spec-053): Standardize API with DTOs and Global Exception Handling

## 📋 Summary

### 배경 및 목적
- **목적**: API의 요청/응답 구조를 표준화하고, 일관된 예외 처리를 통해 시스템 안정성을 높이기 위함.
- **문제점**: 
    - 기존에는 `dict`를 반환하거나 DTO 위치가 파편화되어 있었음 (`app/interfaces/api/dto`).
    - 예외 처리가 각 엔드포인트마다 `try-except`로 중복 구현되어 있거나, `DoitException`이라는 모호한 이름을 사용함.
    - API 계층 구조(`v1/endpoints`)와 DTO 구조가 불일치함.

### 주요 변경 사항
- **DTO 표준화**: `app/interfaces/api/v1/dto/` 디렉토리에 `BaseResponse` 및 도메인별 DTO(Jobs, IO, RAG 등) 구현.
- **예외 처리 통합**: `app/interfaces/api/error_handlers.py`에서 전역 예외 처리기 구현 (Custom Exceptions -> HTTP Status 매핑).
- **Clean Architecture 준수**:
    - `DoitException` -> `BaseAppException` (Core)
    - `DomainException` 등 -> `app/domain/exceptions.py`
    - `InfrastructureException` 등 -> `app/infrastructure/exceptions.py`
- **구조 개선**: `app/interfaces/api/dto` 제거 및 `v1/dto`로 통합.

## 🎯 Key Review Points
1. **Exception Hierarchy**: `BaseAppException` (Core) -> `DomainException` (Domain) / `InfrastructureException` (Infra) 상속 구조 확인.
2. **DTO Usage**: API 엔드포인트들이 `BaseResponse`로 감싸진 데이터를 반환하는지, 명시적 매핑(`map_job_to_response` 등)이 적절한지.
3. **Circular Import**: 예외 클래스 이동으로 인한 순환 참조 문제 여부 (현재 테스트로 검증됨).

## 🧪 Verification

### Automated Tests
```bash
uv run pytest tests/
```
**테스트 결과 요약:**
- ✅ `tests/unit/interfaces/api/dto/test_jobs.py`: DTO 매핑 검증 통과
- ✅ `tests/integration/tdd/test_api_jobs.py`: Jobs API 엔드포인트 동작 검증 통과
- ✅ `tests/integration/test_error_handling.py`: 전역 예외 처리(404, 409, 500) 동작 검증 통과
- ✅ 전체 테스트 슈트 통과 (Unit: 152 pass, Integration: 12 pass)

### Manual Verification (Scenarios)
1. **Swagger UI 확인**: `/docs` 접속 시 Schemas 탭에 `JobResponse`, `BaseResponse` 등이 정상 표시됨.
2. **에러 응답 확인**: 존재하지 않는 Job ID 요청 시 `{"status": "error", "error_code": "ENTITY_NOT_FOUND", ...}` 응답 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/interfaces/api/v1/dto/*.py`: 각 도메인별 Response/Request DTO 정의
- `app/interfaces/api/error_handlers.py`: 전역 예외 핸들러
- `app/domain/exceptions.py`: 도메인 예외 정의
- `app/infrastructure/exceptions.py`: 인프라 예외 정의
- `tests/integration/test_error_handling.py`: 에러 핸들링 테스트

### 🛠 Modified Files
- `app/core/exceptions.py`: `DoitException` -> `BaseAppException` 변경 및 하위 예외 제거
- `app/interfaces/api/v1/endpoints/*.py`: DTO 적용 및 `try-except` 제거 (전역 핸들러 위임)
- `tests/*`: 변경된 예외 및 DTO 경로 반영

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료 (Pre-commit)
