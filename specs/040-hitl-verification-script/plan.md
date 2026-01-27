# Implementation Plan: Spec 040 - Real-World HITL Verification Script

## 📋 Branch Strategy
- `feature/spec-040-hitl-script`

## 🛑 User Review Required
> [!CAUTION]
> **과금 주의**: 이 스크립트는 실제 Google Gemini API를 호출합니다. 반복 실행 시 토큰 비용이 발생할 수 있습니다.

> [!NOTE]
> **검증 범위**: 이 스크립트는 `AdminAgent`의 HITL 로직 검증에 집중하므로, `RAGService`의 복잡한 검색 로직 일부는 단순화될 수 있습니다. (단, LLM은 실제를 사용)

## 🎯 Core Strategy

### 1. Minimal "Real" Architecture
전체 `main.py`를 띄우는 것은 무겁고 설정이 복잡하므로, 필요한 컴포넌트만 조립하는 "Standalone Script" 방식으로 구현합니다.

| Component | Strategy |
|:---:|:---|
| **Brain** (LLM) | `ChatGoogleGenerativeAI` **(Real)** |
| **Agent** | `AdminAgent` **(Real Logic)** |
| **Checkpointer** | `MemorySaver` (In-Memory for Test speed) |
| **Tools** | `RAGService`, `IngestionService` (Real but configured for test) |
| **Interface** | `Python `input()` (Console CLI)` |

### 2. Interactive Loop Pattern
단순한 1회성 실행이 아니라, `while` 루프를 돌며 사용자의 입력을 받아 `stream`을 제어하는 구조를 채택합니다.

```python
# Pseudo Code Structure
while True:
    user_input = input("User: ")
    # ...
    
    # HITL Toggle Support
    hitl_enabled = input("HITL Mode (y/n)? ") == "y"
    
    # 1. Run until interrupt
    inputs = {"messages": [HumanMessage(...)], "hitl_enabled": hitl_enabled}
    async for event in graph.astream(inputs, ...):
        print(event)
        
    # 2. Check if interrupted via Snapshot
    snapshot = graph.get_state(config)
    if snapshot.next:
        print("⏸️  Agent Paused. Waiting for feedback.")
        feedback = input("Feedback: ")
        # 3. Resume
        graph.update_state(config, {"messages": [HumanMessage(content=feedback)]})
        async for event in graph.astream(None, config): # Resume
             print(event)
```

## 📂 Proposed Changes

### [New Script] `scripts/verify_hitl_real.py`

#### [NEW] `scripts/verify_hitl_real.py`
실제 환경과 동일하게 `AdminAgent`를 구성하되, 검증 편의성을 위한 CLI 래퍼를 구현합니다. `AdminAgent` 내부 로직(`route_after_search`)이 `hitl_enabled` 플래그에 따라 `human_review` 노드로 분기하는지 검증합니다.

```python
import asyncio
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from app.domain.services.admin_agent import AdminAgent
# ... imports ...

async def main():
    # 1. Init
    agent = AdminAgent(...)
    workflow = agent.build_workflow(checkpointer=MemorySaver())
    
    # 2. Test Loop
    # ...
```

## 🧪 Verification Plan

### Automated Checks
스크립트 파일 자체의 무결성을 확인합니다.
```bash
# Linting & Formatting
uv run ruff check scripts/verify_hitl_real.py
uv run ruff format scripts/verify_hitl_real.py

# Syntax Check
uv run python -m py_compile scripts/verify_hitl_real.py
```

### Manual Verification (Interactive Scenarios)

#### Scenario A: HITL Disabled (Fast Flow)
1. **Command**: `uv run python scripts/verify_hitl_real.py`
2. **Action**: `HITL Mode: n` 입력 -> 질문 `"RAG가 뭐야?"` 입력
3. **Expectation**:
    - 중간 멈춤(Interrupt) 없이 즉시 답변 생성.
    - 로그에 `State Keys` 확인 시 `hitl_enabled: False` 확인.

#### Scenario B: HITL Enabled (Interrupt & Resume)
1. **Command**: `uv run python scripts/verify_hitl_real.py`
2. **Action**: `HITL Mode: y` 입력 -> 질문 `"RAG가 뭐야?"` 입력
3. **Expectation**:
    - 답변 생성 직전/후 `"⏸️ Paused (HITL)"` 메시지와 함께 대기.
    - `input()` 프롬프트 활성화.
4. **Action**: `"조금 더 요악해서 말해줘"` (Feedback) 입력
5. **Expectation**:
    - Agent가 Feedback을 반영하여 다시 생각(`Thinking...`) 후 답변 수정.
    - 최종 답변 출력 후 종료.

#### Scenario C: State Consistency
1. **Check**: 로그에 출력된 `Snapshot` 정보 확인.
    - `thread_id`가 유지되는가?
    - `messages` 리스트에 사용자 피드백이 추가되었는가?

