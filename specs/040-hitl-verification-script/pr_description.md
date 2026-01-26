feat(spec-040): real-world hitl verification script

## 📋 Summary
Human-in-the-Loop (HITL) 기능의 작동 여부(Interrupt -> Resume)를 **실제 LLM 및 LangGraph 로직** 상에서 검증하는 스크립트 `scripts/verify_hitl_real.py`를 추가했습니다.
기존에는 Admin UI를 통해서만 검증 가능했던 HITL 흐름을, 독립된 스크립트로 자동화하여 백엔드 로직의 건전성을 빠르게 진단할 수 있게 되었습니다.

## 🎯 Key Review Points
1. **Real-World Verification**: Mock을 사용하지 않고 `LangChainLLMAdapter`와 `Google Gemini` 실제 모델을 연동하여 테스트합니다.
2. **Interrupt Simulation**: `retry_count`와 `error` 상태를 강제로 주입하여 `human_review` 노드 진입(Interrupt)을 유도합니다.
3. **Resume Logic**: `update_state`를 통해 상태를 수정한 후 그래프 실행을 재개(Resume)하여 최종 결과가 반영되는지 확인합니다.

## 🧪 Verification
### Automated Tests
```bash
uv run python scripts/verify_hitl_real.py
```

### Manual Verification
1. 위 명령어를 실행합니다.
2. 로그 출력에서 다음 항목을 확인합니다:
   - `✅ SUCCESS: Graph interrupted at 'human_review' as expected!`
   - `✏️ State Updated. Resuming...`
   - `🎉 HITL Verification COMPLETE`

## 📦 Files Changed

### 🆕 New Files
- `scripts/verify_hitl_real.py`: HITL 검증을 위한 독립 실행형 스크립트

### 🛠 Modified Files
- 없음

### 🗑 Deleted Files
- 없음

**Total:** 1 files changed

## ✅ Definition of Done
- [x] 스크립트 실행 시 HITL 시나리오(Interrupt -> Resume)가 에러 없이 완주됨
- [x] 실제 LLM 연동 및 상태 저장(MemorySaver) 동작 확인
