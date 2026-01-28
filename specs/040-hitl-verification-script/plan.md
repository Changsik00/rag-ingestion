# Implementation Plan: Spec-040

## 📋 Branch Strategy
- `feature/040-hitl-verification-fix`

## 🛑 User Review Required
<!-- Korean: Critical items requiring explicit user approval before proceeding -->
- 없음 (Tooling 작업)

## 🎯 Core Strategy
<!-- Korean: Key architectural decisions and reasoning -->
- **Standalone Script**: 기존 `scripts/` 디렉토리에 독립적인 실행 스크립트를 배치하여, 운영 환경이나 CI/CD 파이프라인에서 필요 시 가볍게 실행할 수 있도록 함.
- **Real LLM Interaction**: Mock을 사용하지 않고 `models/gemini.py` 등 실제 구현체를 사용하여 통합성을 검증함.
- **Interrupt Simulation**: `Command`나 특정 State조건을 이용하여 인위적으로 Interrupt 상황을 만들거나, 실제 로직 상의 Interrupt 조건을 트리거함.

## 📂 Proposed Changes
<!-- Group by Component -->

### [Infrastructure]
#### [MODIFY] `app/infrastructure/storage/chroma.py`
- **Fix Embedding Model**: `models/embedding-001` -> `models/text-embedding-004` (Deprecated model caused 404).

### [Core Domain]
#### [MODIFY] `app/domain/ingestion/state.py`
- `IngestionState`에 `hitl_enabled: bool` 필드 추가

#### [MODIFY] `app/infrastructure/brain/graph.py`
- `route_after_validation` 함수 수정: `hitl_enabled`가 True이면 검증 결과와 상관없이(혹은 성공 시에도) `human_review`로 분기하도록 로직 수정.

### [API & Frontend]
#### [MODIFY] `app/interfaces/api/v1/endpoints/admin/rag.py`
- `ask_agent` 엔드포인트 payload에 `hitl_enabled` 파라미터 수신 및 `input_state`에 주입.

#### [MODIFY] `admin/pages/4_RAG_Playground.py`
- `st.toggle` 값을 API 호출 시 payload에 포함.

### [Tooling]
#### [NEW] `scripts/verify_hitl_real.py`
<!-- Korean: HITL 흐름 검증 스크립트 -->
```python
import asyncio
from app.infrastructure.brain.graph import create_graph
# ... imports ...

async def main():
    # 1. Setup Graph with Checkpointer
    # 2. Start Workflow
    # 3. Detect Interrupt
    # 4. Resume Workflow
    # 5. Verify Result
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

## 🧪 Verification Plan

### Automated Tests
- 본 작업 자체가 검증 스크립트를 작성하는 것이므로, 해당 스크립트의 성공 실행이 검증임.
```bash
python scripts/verify_hitl_real.py
```
- **Expected Result**: No `404` errors, successful interruption, and resumption.

### Manual Verification
- 스크립트 실행 로그를 통해 "Interrupt Detected" 및 "Resuming..." 로그 확인.
