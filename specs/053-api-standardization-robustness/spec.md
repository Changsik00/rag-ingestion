# Spec-053: API Standardization & Robustness

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
현재 `app/interfaces/api/` 내부의 엔드포인트들은 응답 형식(Response Schema)이 정의되지 않은 상태로 딕셔너리를 직접 반환하거나, `try-except` 블록에서 모든 예외를 `500 Internal Server Error`로 처리하는 "Catch-All" 패턴이 만연해 있습니다.

### 문제점
1.  **계약 부재**: Swagger/OpenAPI 문서가 생성되지 않아 클라이언트가 응답 구조를 예측할 수 없습니다.
2.  **타입 불안정**: 내부 구현 변경이 API 응답 구조를 예고 없이 변경시킬 위험이 높습니다.
3.  **디버깅 어려움**: `ValueError` 같은 단순 클라이언트 에러도 500 에러로 둔갑하여, 실제 시스템 장애와 사용자 실수를 구분하기 어렵습니다.
4.  **일관성 결여**: `ingest.py`와 `jobs.py` 등 파일마다 응답 처리 방식이 제각각입니다.

### 해결 방안
1.  **Response DTO 도입**: 모든 입/출력 데이터를 Pydantic `BaseModel`로 정의하여 명시적인 계약을 수립합니다.
2.  **Standard Response Envelope**: `JobResponse`, `ErrorResponse` 등 공통된 응답 래퍼를 정의하여 일관성을 확보합니다.
3.  **Global Exception Handler**: 개별 핸들러의 `try-except`를 제거하고, `middleware` 또는 `exception_handler` 수준에서 에러를 중앙 처리합니다.

## 📊 개념도 (Conceptual Architecture)

```mermaid
flowchart LR
    Client -->|Request| GlobalExceptionHandler
    GlobalExceptionHandler -->|Safe Request| APIRouter
    APIRouter -->|DTO Validation| Endpoint
    Endpoint -->|Domain Logic| Service
    Service -->|Result| Endpoint
    Endpoint -->|Response DTO| Client
    
    subgraph "Before"
    Endpoint_Old[Endpoint (Dict Return)] -->|500 Error| Client_Old[Client (Confusion)]
    end
```

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **DTO 정의**: `app/interfaces/api/dto/` 패키지에 요청/응답 모델을 정의한다.
    *   `JobResponse`, `ThreadResponse`, `JobStatusResponse` 등
2.  **엔드포인트 리팩토링**: `app/interfaces/api/v1/endpoints/*.py`의 모든 핸들러가 DTO를 반환하도록 수정한다.
3.  **에러 핸들링 표준화**: 커스텀 예외 클래스(`DomainException` 등)를 정의하고, 이를 HTTP 상태 코드로 매핑하는 핸들러를 구현한다.

### Non-Functional Requirements
1.  **Backward Compatibility**: 기존 API 경로 유지 (Payload 구조 변경은 허용하되, 치명적인 파괴는 최소화).
2.  **Documentation**: `/docs` (Swagger UI)에서 스키마가 올바르게 표시되어야 한다.

## ✅ Definition of Done
1.  모든 API 엔드포인트가 `response_model`을 명시하고 있다.
2.  `try: ... except Exception:` 패턴이 엔드포인트 레벨에서 제거되었다.
3.  성공/실패 시의 응답 JSON 구조가 Swagger 문서와 일치한다.
4.  기존 테스트(`tests/unit/interfaces/api/`)가 수정된 구조에 맞게 통과한다.
