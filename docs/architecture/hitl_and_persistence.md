# HITL Strategy & State Management Architecture

## 1. HITL (Human-in-the-Loop) Strategy

### 1.1 Design Pattern: "Draft Review" vs. "Permission"
본 프로젝트(RAG Playground)는 **"Quality Review (품질 검수)"** 모델, 즉 **Draft Review** 패턴을 채택했습니다.

| Feature | Draft Review (Current) | Permission (Authorization) |
| :--- | :--- | :--- |
| **목적** | 생성된 답변의 **품질 향상** 및 정교화 | 위험한 작업의 **실행 승인** 및 통제 |
| **Workflow** | Draft 생성 → 사람 검토 → **수정(Feedback)** or 확정(Confirm) | 실행 요청 → 사람 승인 → **거절(Reject)** or 승인(Approve) |
| **적합 사례** | RAG 답변, 문서 요약, 코드 생성 | 이메일 전송, DB 삭제, 결제 실행 |
| **실패 비용** | 낮음 (그냥 다시 만들면 됨) | 높음 (되돌릴 수 없음) |

**채택 이유**:
RAG 시스템의 목표는 "정확하고 유용한 정보 제공"입니다. Agent가 먼저 최선을 다해 답변(Draft)을 작성하고, 사용자가 이를 검수하여 부족한 점을 보완(Feedback)하는 방식이 **상호작용을 통한 성능 향상**에 가장 효과적이기 때문입니다.

### 1.2 HITL Workflow Logic
구현된 HITL 흐름은 **"Feedback Loop (순환 구조)"**를 핵심으로 합니다.

1.  **Generate Draft**: `search_node`가 답변을 생성하고 `human_review` 노드 진입 전 멈춥니다(`interrupt_before`).
2.  **User Action**:
    *   **Confirm**: 상태 변경 없이 재개(`resume`) → `END`로 이동하여 완료.
    *   **Revise (Feedback)**: 피드백 내용을 `HumanMessage`로 상태에 추가 → 재개.
3.  **Loop Back**: `AdminAgent`는 마지막 메시지가 사람의 피드백임을 감지하고, 종료하는 대신 **`router` 노드로 되돌아갑니다.**
4.  **Regenerate**: 피드백을 반영하여 다시 검색 및 생성을 수행, 새로운 Draft를 제시합니다.

---

## 2. State Management & Persistence (LangGraph)

LangGraph는 **State(상태)**를 중심으로 동작하며, 이 상태를 영구적으로 저장하고 관리하기 위해 **Checkpointer**를 사용합니다.

### 2.1 Why Persistence? (왜 저장하는가?)
HITL 대화는 **"멈춤(Pause)"**과 **"재개(Resume)"**가 핵심입니다.
*   Agent가 멈췄을 때의 **모든 문맥(대화 이력, 검색 결과, 내부 변수)**을 어딘가에 저장해두지 않으면, 사용자가 10분 뒤에 "승인"을 눌렀을 때 Agent는 자신이 무엇을 하고 있었는지 잊어버리게 됩니다.
*   Checkpointer는 이 "시점"의 스냅샷을 저장하여 언제든 해당 지점에서 다시 시작할 수 있게 해줍니다.

### 2.2 Storage Strategies

#### 💾 MemorySaver (In-Memory)
*   **저장소**: RAM (Python Dictionary)
*   **특징**: 프로그램이 종료되면 데이터가 사라짐.
*   **용도**: 빠른 단위 테스트, 임시 검증, 로컬 개발 초기 단계.

#### 💽 AsyncSqliteSaver (Persistent Disk)
*   **저장소**: SQLite 파일 (`checkpoints.sqlite`)
*   **특징**: 프로그램이 재시작되어도 데이터가 유지됨. 비동기 I/O 지원 (`aioiosqlite`).
*   **용도**: **운영 환경(Production)**, 실제 데모. 서버가 재시작되어도 사용자의 대화 흐름(HITL 상태)을 복구할 수 있음.

> **주의**: `AsyncSqliteSaver`는 DB I/O가 발생하므로 반드시 `await` 키워드를 사용하여 비동기적으로 접근해야 합니다. 동기 메서드(`update_state`)를 호출하면 스레드 차단 에러가 발생합니다.

### 2.3 Thread ID & Namespace
*   **Thread ID**: 사용자의 파이프라인 세션을 구분하는 고유 키. (예: `playground-a1b2c3d4`)
*   **Namespace 분리**: `AdminAgent`(HITL 관리)와 `RAGService`(내부 검색)가 동일한 Checkpointer를 공유할 경우, 상태 충돌이 발생할 수 있습니다. 이를 방지하기 위해 `RAGService` 호출 시에는 `rag-{thread_id}`와 같이 접두어를 붙여 별도의 "가상 스레드"를 사용합니다.

---

## 3. Core Logic & Implementation Checks

### 3.1 AdminAgent (`app/domain/services/admin_agent.py`)
*   **`build_workflow`**: 그래프 구조 정의. `human_review` 노드에 조건부 엣지(`route_after_review`)를 추가하여 피드백 루프를 구현.
*   **`interrupt_before=["human_review"]`**: 이 설정이 있어야 Agent가 완료 전에 멈추고 사용자의 입력을 기다립니다.

### 3.2 API Endpoint (`apis/.../rag.py`)
*   **`resume_session`**: 사용자의 `Confirm`/`Revise` 요청을 처리.
    *   **Feedback**: `await workflow.aupdate_state()`로 메시지 추가 후 `ainvoke`.
    *   **Confirm**: 변경 없이 `ainvoke(None)` 호출 (그대로 진행).

### 3.3 Debugging Points
*   **"Synchronous calls..." Error**: 비동기 Checkpointer 사용 시 동기 메서드 호출 금지.
*   **UI Inconsistency**: 화면의 Debug Info와 실제 답변이 다른 경우, UI 상태 업데이트 로직(Session State sync) 확인 필요.
