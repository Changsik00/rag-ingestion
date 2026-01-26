# Spec-040: Real-World HITL Verification Script

## 📋 배경 및 문제 정의 (Background & Problem)
<!-- Korean: Why is this needed? What is the current problem? -->
현재 HITL(Human-in-the-loop) 기능은 `checkpoints.sqlite`와 연동되어 구현되어 있으나, 이를 검증하기 위해서는 복잡한 UI 조작이나 수동 테스트가 필요함.
특히 실제 LLM(Gemini)과의 상호작용 상황에서 Interrupt가 정상적으로 발생하고, Resume이 정확히 동작하는지 검증하는 자동화된 스크립트가 부재함.
따라서, Mock이 아닌 실제 LLM 환경에서 HITL 전체 흐름(Interrupt -> Resume)을 검증할 수 있는 CLI 스크립트가 필요함.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **Verification Script**: `scripts/verify_hitl_real.py` 작성
2. **Scenario Execution**:
    - LangGraph 인스턴스 초기화 (Checkpointer 포함)
    - 실제 Gemini LLM과 상호작용 시작
    - 강제 Interrupt 유발 (또는 Interrupt가 발생하는 시나리오 명시적 트리거)
    - `interrupt` 상태 감지 및 로그 출력
    - 사용자 입력 또는 자동화된 `resume` 명령 전송
    - 최종 실행 완료 및 결과 확인
3. **Logging**: 각 단계별 상태(State Snapshot) 및 결과 로깅

### Non-Functional Requirements
1. **Security**: 실제 API Key 사용 시 로깅에 Key가 노출되지 않도록 주의
2. **Independence**: 다른 테스트나 DB 상태에 영구적인 영향을 주지 않도록 독립된 Thread ID 사용 권장

## ✅ Definition of Done
1. `python scripts/verify_hitl_real.py` 실행 시 에러 없이 시나리오 완주
2. Interrupt 발생 및 Resume 로그 확인 가능
3. 최종 결과가 정상적으로 생성됨 확인
