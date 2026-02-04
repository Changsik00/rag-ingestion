# refactor(spec-062): convert rag api to clean architecture

## 📋 Summary

### 배경 및 목적
기존의 RAG API(`rag.py`)는 Fast Controller 패턴으로 구현되어 있어, SQL 쿼리, LangGraph 워크플로우 제어, 응답 매핑 로직이 혼재되어 있었습니다.
**Spec 062**에 따라 이를 **Clean Architecture** 원칙에 맞게 리팩토링하여 유지보수성을 높이고, 테스트가 용이한 구조(Thin Controller)로 개선하는 것이 목적입니다.

### 주요 변경 사항
- [x] **Repository Layer 도입**: `PostgresSessionRepository`를 구현하여 SQL 로직 캡슐화
- [x] **Service Layer 강화**: `ConversationalRAGAgent`에 `ask`, `resume` 메서드를 추가하여 LangGraph 실행 로직 위임
- [x] **DTO Mapper 분리**: `ChatResponseMapper`를 도입하여 응답 변환책임 분리
- [x] **Test Reliability**: `conftest.py` 내 `TestClient` Lifespan 관리를 개선하여 DB Pool 에러 해결

## 🎯 Key Review Points
1. **Thin Controller**: `rag.py`에서 비즈니스 로직이 완전히 제거되고 Facade 역할만 수행하는지 확인
2. **Dependency Injection**: `dependencies.py`를 통해 `SessionRepository` 등이 올바르게 주입되는지 확인
3. **Integration Tests**: `test_rag_session_cleanup.py` 등 회귀 테스트가 정상적으로 수정 및 통과되었는지

## 🧪 Verification

### Automated Tests
```bash
uv run pytest tests/integration/functional/
```
**테스트 결과 요약:**
- ✅ `test_rag_session_cleanup.py`: 세션 생성 및 초기화(Repo 동작) 검증 통과
- ✅ `test_api_endpoints.py`: 기존 API 기능 회귀 테스트 통과

### Manual Verification (Scenarios)
1. **RAG 채팅**: RAG Playground에서 질문 입력 -> 정상 답변 반환
2. **세션 초기화**: "Delete History" 버튼 클릭 -> DB에서 체크포인트 삭제 확인

## 📦 Files Changed

### 🆕 New Files
- `app/domain/interfaces/session_repository.py`: 세션 리포지토리 인터페이스
- `app/infrastructure/repositories/postgres_session_repository.py`: Postgres 기반 세션 삭제 구현체
- `app/interfaces/api/v1/dto/mappers.py`: ChatResponse 매핑 로직

### 🛠 Modified Files
- `app/interfaces/api/v1/endpoints/rag.py`: 컨트롤러 로직 간소화 (Facade 패턴 적용)
- `app/application/services/agent.py`: LangGraph 실행 로직(`ask`, `resume`) 추가
- `app/interfaces/api/dependencies.py`: 새로운 리포지토리 의존성 등록
- `tests/integration/conftest.py`: `TestClient` Lifespan Fix

**Total:** 7 files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
