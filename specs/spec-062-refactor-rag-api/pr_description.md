# refactor(spec-062): convert rag api to clean architecture

## 📋 Summary
**Spec 062**에 따라 RAG API(`rag.py`)의 비즈니스 로직과 데이터 액세스 로직을 분리하여 **Clean Architecture**를 적용했습니다.
이제 `rag.py`는 단순한 HTTP 라우터 역할만 수행하며, 복잡한 로직은 Service, Repository, DTO Mapper로 위임됩니다.

## 🛠️ Key Changes
- **Repository Layer 도입**:
  - `SessionRepository` (Interface) 및 `PostgresSessionRepository` (Impl) 추가.
  - `reset_session`의 Raw SQL 로직을 Repository로 이동.
- **Service Layer 강화**:
  - `ConversationalRAGAgent`에 `ask()` 및 `resume()` 메서드 추가.
  - LangGraph 실행(`ainvoke`), Config 설정 로직을 Service 내부로 캡슐화.
- **DTO Mapper 분리**:
  - `ChatResponseMapper`를 도입하여 응답 변환 로직(`map_to_chat_response`)을 분리.
- **Test Infrastructure 개선**:
  - `tests/integration/conftest.py`: `TestClient`의 Lifespan(Startup/Shutdown) 관리를 개선하여 `database.pool` 관련 에러 해결.

## 🧪 Verification
- [x] **Integration Tests**: `test_rag_session_cleanup.py`, `test_api_endpoints.py` 통과 (회귀 테스트 완료).
- [x] **Manual Verification**: RAG Playground에서 채팅 생성 및 세션 초기화 정상 동작 확인.

## 🔔 Review Points
- **Architecture**: `rag.py`가 충분히 얇아졌는지(Thin Controller), 의존성 주입이 올바르게 구성되었는지 확인 부탁드립니다.
- **Legacy Removal**: 기존의 `reset_session` 내 `adelete_thread` 체크 로직 삭제하고 Repository로 통일했습니다.

---
Closes #Spec-062
