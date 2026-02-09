# PR Description: Spec-074

## 🚀 Summary
Clean Architecture의 Dependency Rule을 준수하기 위해 `LLMInterface`를 Application Layer에서 Domain Layer로 이동하였습니다. 이를 통해 도메인 로직의 순수성을 확보하고 계층 간 결합도를 낮추었습니다.

## ✨ Key Review Points
- `app/domain/interfaces/llm_interface.py` 신규 생성 및 인터페이스 정의 이동.
- `app/domain/services/` 내의 `IntentClassifier`, `QueryRewriter` 임포트 경로 수정 (아키텍처 위반 해결).
- `app/infrastructure/` 및 `app/application/` 내의 모든 참조 경로 업데이트.
- 기존 `app/application/interfaces/llm.py` 제거.

## 🧪 Verification Evidence
- **Ruff Check**: `uv run ruff check app/domain` 통과.
- **Unit Tests**: `pytest` 전체 테스트(104개) 통과.
- **Dependency Check**: 도메인 계층 내에서 애플리케이션 계층을 참조하는 코드가 없음을 `grep`으로 확인.

## 📸 Screenshots / Recordings
(N/A - Backend Refactoring)
