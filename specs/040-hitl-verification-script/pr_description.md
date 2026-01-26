feat(spec-040): real-world hitl verification script & toggle fix

## 📋 Summary
1. **HITL Verification Script**: 실제 LLM 및 LangGraph 로직 상에서 HITL 흐름(Interrupt -> Resume)을 검증하는 스크립트 `scripts/verify_hitl_real.py`를 추가했습니다.
2. **Admin HITL Toggle Fix**: Admin UI의 "Enable HITL" 토글이 실제 작동하지 않던 문제를 수정했습니다. `IngestionState`에 `hitl_enabled` 필드를 추가하고, Graph 및 API 전반에 연동했습니다.

## 🎯 Key Review Points
1. **Toggle Logic**: `route_after_validation` 함수에서 `hitl_enabled=True`일 경우 강제로 `human_review`로 분기하는 로직을 추가했습니다.
2. **Real-World Verification**: 검증 스크립트가 토글을 켰을 때 정상적으로 Interrupt 되는지 확인합니다.
3. **Full-Stack Update**: Frontend(Streamlit) -> API(FastAPI) -> Backend(LangGraph) -> State까지 데이터 흐름이 연결되었습니다.
4. **Collision Fix**: `AdminAgent`와 내부 `RAGService` 간 Checkpointer ID 충돌 방지를 위해 Thread ID Namespace(`rag-*`)를 적용했습니다.

## 🧪 Verification
### Automated Tests
```bash
uv run python scripts/verify_hitl_real.py
```

### Manual Verification
#### 1. Script Verification
1. 위 명령어를 실행합니다.
2. 로그 출력에서 다음 항목을 확인합니다:
   - `✅ SUCCESS: Graph interrupted at 'human_review' as expected (Toggle Works)!`
   - `🎉 HITL Verification COMPLETE`

#### 2. Admin UI Verification
1. `uv run streamlit run admin/0_Job_Queue.py` 실행
2. **RAG Playground** 메뉴 이동
3. **Advanced Settings** > **Enable HITL Review** 토글 활성화
4. 질문 입력 후 "Thinking..." 단계에서 멈추는지(Status가 complete로 변하지 않는지) 확인 (현재는 Stop UI가 없으므로 로그나 상태로 확인)

## 📦 Files Changed

### 🆕 New Files
- `scripts/verify_hitl_real.py`: HITL 검증 스크립트 (Updated)

### 🛠 Modified Files
- `app/domain/ingestion/state.py`: `hitl_enabled` 필드 추가
- `app/infrastructure/brain/graph.py`: Routing 로직에 토글 체크 추가 (Ingestion)
- `app/domain/services/admin_agent.py`: Routing 로직에 토글 체크 추가 및 Thread ID 충돌 수정
- `app/interfaces/api/v1/endpoints/admin/rag.py`: API Payload 처리 추가
- `admin/pages/4_RAG_Playground.py`: API 호출 시 토글 값 전달

### 🗑 Deleted Files
- 없음

**Total:** 5 files changed

## ✅ Definition of Done
- [x] 스크립트 실행 시 HITL 시나리오(Interrupt -> Resume)가 에러 없이 완주됨
- [x] Admin HITL Toggle 정상 작동 (Script 검증 완료)
