# Implementation Plan: Spec-062

## 📋 Branch Strategy
- `feature/spec-062-refactor-rag-api`

## 🛑 User Review Required
> [!IMPORTANT]
> - [ ] **Interface Changes**: `ConversationalRAGAgent` 클래스의 `ask` 메서드 시그니처가 변경됩니다. 기존 `build_workflow` 호출 방식은 제거되거나 wrapping 됩니다.

## 🎯 Core Strategy

### Architecture Context
**Strangler Fig Pattern**을 적용하여, 컨트롤러의 로직을 점진적으로 하위 계층(Service, Repository)으로 이동시킵니다.

| Component | Strategy | Reasoning |
|:---:|:---|:---|
| **RAG Controller** | **Thin Controller** | 요청 검증 및 응답 반환에만 집중하고, 로직은 위임합니다. |
| **Session Repository** | **Repository Pattern** | DB 액세스 로직(SQL)을 인프라 계층으로 격리합니다. |
| **RAG Agent Service** | **Facade Pattern** | 복잡한 LangGraph 실행 과정을 `ask`, `resume` 메서드 뒤로 숨깁니다. |

## 📂 Proposed Changes

### [New Layer] Repository

#### [NEW] `app/domain/interfaces/session_repository.py`
- `SessionRepository` 추상 클래스 정의 (`delete_session` 메서드).

#### [NEW] `app/infrastructure/repositories/postgres_session_repository.py`
- `AsyncConnectionPool`을 사용하는 `PostgresSessionRepository` 구현.

### [New Layer] DTO Mapper

#### [NEW] `app/interfaces/api/v1/dto/mappers.py`
- `ChatResponseMapper` 클래스 구현 (`map_graph_output_to_response`).

### [Modified Layer] Service

#### [MODIFY] `app/application/services/agent.py`
- `ask(...)` 메서드 추가: `build_workflow` -> `compile` -> `ainvoke` 과정 캡슐화.
- `resume(...)` 메서드 추가.

### [Modified Layer] API

#### [MODIFY] `app/interfaces/api/v1/endpoints/rag.py`
- `get_session_repository` 의존성 주입.
- `database.pool` 및 `workflow` 직접 사용 코드 제거.
- Service 및 Repository 메서드 호출로 대체.

## 🧪 Verification Plan

### Automated Tests
```bash
# 1. 세션 정리 기능(Cleanup) 검증 (회귀 테스트)
uv run pytest tests/integration/functional/test_rag_session_cleanup.py

# 2. 채팅 및 기타 기능 검증
uv run pytest tests/integration/functional/test_api_endpoints.py
```

### Manual Verification
1.  **Chat**: RAG Playground에서 질문 입력 -> 답변 생성 및 히스토리 누적 확인.
2.  **Reset**: "Delete History" 클릭 -> "Successfully reset" 메시지 확인 -> 재접속 시 히스토리 초기화 확인.
