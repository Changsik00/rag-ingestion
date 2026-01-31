# refactor(spec-051): AI 인프라 계층화 및 네이밍 표준화

## 📋 Summary

### 배경 및 목적
- AI 인프라 구성 요소(LLM 어댑터, 그래프 노드, 오케스트레이터 등)가 파편화되어 있어 유지보수가 어려운 문제를 해결하기 위함.
- 클래스 네이밍을 도메인 개념과 실제 역할에 맞게 표준화하여 코드의 가독성과 일관성을 향상시킴.
- Clean Architecture의 계층 구조를 더욱 엄격히 적용하여 의존성 방향을 명확히 함.

### 주요 변경 사항
- **AI 인프라 계층화**: `infrastructure/ai/` 하위로 구성 요소를 역할별로 재배치
  - `extractors/`: LLM 인터페이스 구현 (e.g., `LangChainExtractor`)
  - `orchestrators/`: 그래프 실행 제어 (e.g., `IngestionOrchestrator`)
  - `nodes/`: 그래프 개별 노드 로직 (e.g., `IngestionNodes`, `logic.py`)
  - `graphs/`: 그래프 워크플로우 정의 (e.g., `IngestionGraph`)
- **네이밍 표준화 (Agent & State)**:
  - `AdminAgent` -> `ConversationalRAGAgent`
  - `AdminState` -> `AgentState`
  - `IngestionState` -> `IngestionGraphState`
  - `RAGState` -> `RAGGraphState`
- **도메인 서비스 및 인터페이스 정제**:
  - `IngestionService` -> `IngestionUseCase`
  - `IntegrityService` -> `Integrity`
  - `FeedbackService` -> `Feedback`
  - `app.infrastructure.storage` -> `app.infrastructure.repositories`
- **API DTO 리팩토링**:
  - `interfaces/api/schemas/` -> `interfaces/api/dto/`

## 🎯 Key Review Points
1. **의존성 주입 로직 (`dependencies.py`)**: 리팩토링 과정에서 발생했던 `Undefined Name` 오류들을 수정하였으며, `SemanticExtractor` 및 `Integrity` 서비스에 올바른 `Orchestrator`가 주입되는지 확인이 필요함.
2. **계층간 네이밍 일관성**: 각 계층(Domain, Application, Infrastructure)의 클래스 명칭이 의도된 책임을 충분히 설명하는지 검토 필요.
3. **테스트 코드 호환성**: 대규모 리팩토링 이후 모든 테스트가 정상적으로 수집되고 실행되는지 확인 완료.

## 🧪 Verification

### Automated Tests
```bash
uv run pytest
```
**테스트 결과 요약:**
- ✅ 190 passed, 64 skipped
- ⚠️ Warnings: 44 (주로 deprecation warning으로 로직 영향 없음)

### Manual Verification (Scenarios)
1. **Ruff Linting**: `uv run ruff check .` 실행 결과 모든 이슈 해결 확인.
2. **Dependency Tree**: `app.interfaces.api.v1.endpoints.admin.rag` 등 주요 엔드포인트에서 리팩토링된 클래스(`ConversationalRAGAgent` 등)가 정상적으로 동작하도록 import 수정 완료.

## 📦 Files Changed
- `app/domain/value_objects/`: 신규 VO 추가 및 모델 반영
- `app/infrastructure/ai/`: AI 구성 요소 계층화 및 이동
- `app/infrastructure/repositories/`: Storage 폴더 이동 및 네이밍 변경
- `app/interfaces/api/dto/`: Schema 폴더 이동 및 네이밍 변경
- (약 200개 이상의 파일 수정 - 대부분 Import 경로 및 클래스명 업데이트)

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
