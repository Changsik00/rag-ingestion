# Check List

- [x] 적절한 제목으로 PR을 생성했나요?
- [x] 변경 사항에 대한 테스트(Automated/Manual)를 수행했나요?
- [x] 문서(spec, plan, task, walkthrough)를 포함했나요?

## Summary
Spec 040 "Real-World HITL Verification Script" 구현 PR입니다.
Mock 객체에 의존하던 기존 테스트의 한계를 극복하고, 실제 LLM(Gemini)과 AdminAgent 로직을 사용하여 "Human-in-the-loop(HITL)" 메커니즘을 검증하는 독립 스크립트를 추가했습니다.

## Changes

### 1. Verification Script (`scripts/verify_hitl_real.py`)
- **Real Component Init**: `Neo4jStorage`, `ChromaStorage`, `AdminAgent` 등 실제 컴포넌트를 초기화하여 환경 호환성을 확인합니다.
- **Interactive CLI**: 사용자로부터 입력을 받고, 스트리밍 응답을 출력하는 CLI 환경을 구축했습니다.
- **HITL Toggle**: 사용자가 HITL 활성화 여부(y/n)를 선택할 수 있게 하여, Admin UI의 토글 기능을 시뮬레이션했습니다.
- **Mock Service Injection**: AdminAgent의 HITL 로직 검증에 집중하기 위해 검색 서비스(`RAGService`)는 부분적으로 Mocking하여 실행 속도와 격리성을 확보했습니다.

### 2. Documentation (`specs/040-hitl-verification-script/`)
- `spec.md`, `plan.md`, `task.md`: 구현 계획 및 검증 시나리오 상세화.
- `walkthrough.md`: 시나리오 A(HITL OFF) 및 B(HITL ON) 검증 결과 및 로그 스크린샷 포함.

## Test Results
`scripts/verify_hitl_real.py` 실행을 통해 다음 시나리오를 통과했습니다.
- **Scenario A (HITL OFF)**: 질문 -> 검색 -> 답변 (Non-stop) ✅
- **Scenario B (HITL ON)**: 질문 -> 검색 -> **PAUSE** -> 사용자 피드백(Approved) -> **RESUME** -> 답변 ✅
