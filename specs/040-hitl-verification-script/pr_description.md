feat(spec-040): real-world hitl verification script

## 📋 Summary
Human-in-the-Loop (HITL) 기능의 작동 여부(Interrupt -> Resume)를 **실제 LLM 및 LangGraph 로직** 상에서 검증하는 스크립트 `scripts/verify_hitl_real.py`를 추가했습니다.
UI를 통하지 않고도 백엔드 로직의 건전성을 빠르게 진단할 수 있습니다.

## 🎯 Key Review Points
1. **Mock 사용 배제**: `MockLLM`이 아닌 실제 `LangChainLLMAdapter`와 `Google Gemini` 모델을 사용하여 테스트의 신뢰도를 높였습니다.
2. **State Injection**: 강제로 `human_review` 상태를 유발하기 위해 `initial_input`에 `retry_count`와 `error`를 주입하는 방식을 사용했습니다.
3. **Resume Logic**: `update_state`를 통해 오류가 수정된 데이터를 주입하고 그래프가 정상적으로 재개되는지 확인했습니다.

## 🧪 Verification
### Automated Tests
```bash
uv run python scripts/verify_hitl_real.py
```
실행 결과 `✅ SUCCESS: Graph interrupted at 'human_review' as expected!` 로그 및 최종 완료 로그 확인.

## 📦 Files Changed

### 🆕 New Files
- `scripts/verify_hitl_real.py`: HITL 검증을 위한 독립 실행형 스크립트

## ✅ Definition of Done
- [x] 스크립트 실행 시 HITL 시나리오(Interrupt -> Resume)가 에러 없이 완주됨
