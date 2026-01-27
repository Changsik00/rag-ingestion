# test(spec-040): real-world hitl verification script

## 📋 Summary

### 배경 및 목적
현재 Admin Dashboard의 "HITL(Human-in-the-loop) 활성화" 버튼은 존재하지만, 실제 백엔드 로직에서 이 토글이 올바르게 동작하는지 검증할 수 있는 수단이 부족했습니다.
기존 테스트(`scripts/verify_admin_agent.py`)는 Mock 객체를 사용하여 실제 LLM과의 상호작용 및 State 관리(Checkpointer)를 완벽하게 대변하지 못했습니다.

이에 **실제 LLM(Gemini)과 AdminAgent, 그리고 In-Memory Checkpointer**를 결합하여, 사용자의 개입(Interrupt/Resume) 과정을 시뮬레이션하고 검증할 수 있는 독립형 스크립트(`scripts/verify_hitl_real.py`)를 구현했습니다.

### 주요 변경 사항
1.  **Verification Script 추가** (`scripts/verify_hitl_real.py`)
    *   `AdminAgent`와 실제 `ChatGoogleGenerativeAI` 연결.
    *   `Neo4jStorage`, `ChromaStorage` 등 실제 인프라 컴포넌트 초기화.
    *   CLI 기반의 Interactive Loop 구현 (HITL Toggle 지원).
    *   `RAGService`는 Mocking하여 Agent 로직 검증에 집중 (검색 복잡도 격리).

2.  **문서화** (`specs/040-hitl-verification-script/`)
    *   `spec.md`: 요구사항 및 시나리오 정의.
    *   `plan.md`: 구현 계획 상세.
    *   `walkthrough.md`: 실행 결과 및 로그 증적.

## 🎯 Key Review Points
1.  **HITL 로직의 정확성**:
    *   HITL Toggle `OFF` -> 중단 없이 실행 완료.
    *   HITL Toggle `ON` -> `human_review` 노드 앞에서 `__interrupt__` 발생 -> 사용자 피드백(Resume) -> 실행 완료.
    *   이 흐름이 스크립트(`main` 함수 내 loop)에서 올바르게 처리되고 있는지 확인 부탁드립니다.

2.  **실제 환경 호환성**:
    *   `get_real_services()` 함수에서 실제 DB Driver와 LLM Client를 생성하는 방식이 `app/main.py`의 구조와 유사한지(즉, 현실적인지) 검토가 필요합니다.

## 🧪 Verification

### Automated Tests
1.  **전체 테스트 회귀 점검**:
    ```bash
    uv run pytest -v
    ```
    *(기존 비즈니스 로직에 영향을 주지 않는 독립 스크립트 추가이므로, 기존 테스트는 모두 통과해야 함)*

2.  **스크립트 린트/문법 점검**:
    ```bash
    uv run ruff check scripts/verify_hitl_real.py
    uv run python -m py_compile scripts/verify_hitl_real.py
    ```

### Manual Verification (Checkpoint)
이 PR의 핵심 검증은 **스크립트 실행**을 통해 이루어집니다. 리뷰어는 다음 명령어로 직접 시나리오를 테스트할 수 있습니다.

#### 🚀 실행 명령어
```bash
PYTHONPATH=. uv run python scripts/verify_hitl_real.py
```

#### ✅ Checkpoint 1: HITL Mode OFF (자동 통과)
1.  `Enable HITL? (y/n)` 질문에 **`n`** 입력.
2.  질문 입력 (예: "안녕").
3.  **기대 결과**: "Agent Paused" 메시지 없이 즉시 최종 답변 출력.

#### ✅ Checkpoint 2: HITL Mode ON (일시 정지 & 재개)
1.  `Enable HITL? (y/n)` 질문에 **`y`** 입력.
2.  질문 입력 (예: "테스트").
3.  **기대 결과**:
    *   `⏸️ Agent Paused! Next Node: ('human_review',)` 메시지 출력.
    *   `Feedback` 입력 대기.
4.  Feedback 입력 (예: "Approved").
5.  **기대 결과**:
    *   `▶️ Resuming Agent...` 출력.
    *   `human_review` 노드 실행 후 최종 답변 출력.

## 📦 Files Changed
- `scripts/verify_hitl_real.py`: 신규 검증 스크립트.
- `specs/040-hitl-verification-script/*`: 관련 문서 (Spec, Plan, Task, Walkthrough).

## ✅ Definition of Done
- [x] `verify_hitl_real.py` 구현 및 실행 확인
- [x] Scenario A/B 검증 완료 (Walkthrough 참고)
- [x] 기존 테스트(`pytest`) 회귀 없음 확인
- [x] 문서화 완료 (`walkthrough.md` 포함)
