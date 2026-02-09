# feat(spec-074): llm interface clean architecture compliance

## 📋 Summary

### 배경 및 목적
Clean Architecture의 Dependency Rule을 준수하기 위해 `LLMInterface`를 Application Layer에서 Domain Layer로 이동하였습니다. 이를 통해 도메인 계층이 외부 계층(Application, Infrastructure)에 의존하는 아키텍처 위반 문제를 해결하고 고수준 정책의 독립성을 확보합니다.

### 주요 변경 사항
- [x] **도메인 인터페이스 이동**: `app/application/interfaces/llm.py` -> `app/domain/interfaces/llm_interface.py`
- [x] **의존성 방향 교정**: `IntentClassifier`, `QueryRewriter` 등 도메인 서비스가 도메인 내 인터페이스를 참조하도록 수정
- [x] **참조 업데이트**: 애플리케이션(`SemanticExtractor`), 인프라(`IngestionGraph`, `LLMFactory`) 및 테스트 코드의 모든 참조 경로 업데이트
- [x] **레거시 제거**: 더 이상 사용되지 않는 `app/application/interfaces/llm.py` 삭제

## 🎯 Key Review Points
1. **Domain Layer Independence**: `app/domain` 하위 코드들이 더 이상 `app/application`을 참조하지 않는지 확인 부탁드립니다.
2. **Type Compatibility**: `LLMInterface`와 `LLMInvoker`가 도메인 인터페이스로 이동하며 발생한 타입 힌트 문제들을 전수 점검하였습니다.

## 🧪 Verification

### Automated Tests
```bash
# 전체 테스트 실행
uv run pytest

# 도메인 레이어 의존성 규칙 위반 검사
uv run ruff check app/domain
```
**테스트 결과 요약:**
- ✅ `pytest`: 104 passed (Unit, Integration, E2E)
- ✅ `ruff`: No violations found

### Manual Verification (Scenarios)
1. **의존성 전수 조사**: `grep -r "app.application" app/domain` 실행 시 결과 없음 확인.
2. **임포트 경로 확인**: `grep -r "app.application.interfaces.llm" .` 실행 시 결과 없음 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/interfaces/llm_interface.py`: `LLMInterface`, `LLMInvoker` 및 관련 데이터 구조 정의 이동

### 🛠 Modified Files
- `app/domain/services/intent_classifier.py`: 임포트 경로 수정
- `app/domain/services/query_rewriter.py`: 임포트 경로 수정
- `app/application/services/semantic_extractor.py`: 임포트 경로 수정
- `app/infrastructure/ai/ingestion_orchestrator.py`: 임포트 경로 수정
- `app/infrastructure/ai/ingestion_graph.py`: 임포트 경로 수정
- `app/infrastructure/ai/ingestion_nodes.py`: 임포트 경로 수정
- `app/infrastructure/factories/llm_factory.py`: 임포트 경로 수정
- `tests/`: 9개 이상의 테스트 파일 및 유틸리티 수정

**Total:** 20+ files changed

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
