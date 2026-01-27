# Spec 040: Real-World HITL Verification Script

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
**Spec 022**를 통해 HITL 메커니즘을 구현했고, Admin Dashboard에는 이미 `HITL 활성화` 토글 버튼이 존재합니다. 그러나 현재 검증 스크립트(`scripts/verify_admin_agent.py`)는 Mock 객체를 사용하며, 실제 LLM과 연동된 상태에서 이 토글의 작동 여부(ON일 때 멈추고, OFF일 때 통과하는지)를 확실하게 보장하지 못하고 있습니다.

### 해결 방안
Mock이 아닌 **실제 LLM(Gemini Pro)과 AdminAgent**를 사용하는 스크립트(`scripts/verify_hitl_real.py`)를 작성합니다.
특히 **사용자가 "HITL 모드"를 켰을 때와 껐을 때 Agent의 행동이 달라지는지**를 중점적으로 검증하여, Admin UI의 버튼이 실제 백엔드 로직에 올바르게 반영될 수 있음을 증명합니다.

## 🎯 요구사항 (Requirements)

### Functional Requirements
1.  **HITL Toggle Verification**:
    - 스크립트 실행 시 HITL 모드 ON/OFF를 선택할 수 있어야 함.
    - **OFF**: 중단 없이 질문 -> 답변 전 과정이 자동 실행되어야 함.
    - **ON**: 답변 생성 직전/직후(로직에 따라) `interrupt`가 발생하고 사용자의 승인을 기다려야 함.
2.  **Real LLM Integration**: 
    - `ChatGoogleGenerativeAI` 사용.
3.  **Interactive Resume**:
    - 중단 상태에서 사용자 피드백(텍스트) 입력 시 `update_state`를 통해 반영되고 진행이 재개되어야 함.

### Non-Functional Requirements
1.  **Safety**: 과금 방지(무한 루프 제한).
2.  **Simplicity**: 복잡한 웹 서버 없이 단일 스크립트로 동작.

## ✅ Definition of Done
1.  `scripts/verify_hitl_real.py` 실행 가능.
2.  **Scenario 1 (HITL OFF)**: 질문 입력 시 멈춤 없이 최종 답변 출력.
3.  **Scenario 2 (HITL ON)**: 질문 입력 시 "Paused" 상태 진입 -> 사용자 입력 -> 최종 답변 출력.
