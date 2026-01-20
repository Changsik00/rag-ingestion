# Walkthrough: Spec-023 Reasoning Context & Failure Analysis

## 🎯 Implementation Overview
본 변경사항은 LangGraph의 재시도 로직에 "사고의 맥락(Reasoning Context)"을 주입하여, 에이전트가 단순히 반복하는 것이 아니라 "왜 실패했는지" 이해하고 더 똑똑하게 재시도하도록 개선했습니다.

## 📝 Key Changes

### 1. State Definition (`app/domain/ingestion/state.py`)
- **`FailureHypothesis` (New)**: 실패 원인(`cause`), 설명(`description`), 잘못된 전제(`invalid_assumptions`)를 구조화.
- **`BacktrackingContext` (New)**: 실패 추적을 위한 상태 컨테이너 추가.

### 2. Failure Analysis Logic (`app/infrastructure/brain/nodes.py`)
- **`analyze_failure` Node**: 검증 실패(`error` or `last_feedback`) 시 실행되어, Rule-based 로직으로 실패 원인을 분석하고 가설을 수립합니다.
- **Improved Prompting**: `extract_metadata` 단계에서 `FailureHypothesis`가 존재하면, 프롬프트 상단에 "FAILURE ANALYSIS" 섹션을 주입합니다.

### 3. Graph Logic (`app/infrastructure/brain/graph.py`)
- **Retry Loop 변경**: 
    - 기존: `Extract` -> `Validate` -> (Fail) -> `Logic` -> `Extract`
    - 변경: `Extract` -> `Validate` -> (Fail) -> **`Analyze`** -> `Logic` -> `Extract`

## 🧪 Verification Results

### Automated Tests
- **Unit Tests**:
    - `test_reasoning_state.py`: State 구조 및 타입 검증 (Pass)
    - `test_analysis_node.py`: 에러/피드백에 따른 가설 생성 로직 검증 (Pass)
    - `test_prompt_injection.py`: 프롬프트 내 분석 내용 주입 여부 검증 (Pass)
- **Integration Tests (BDD)**:
    - `test_reasoning_flow.py`: 전체 재시도 흐름(`Validate` -> `Analyze` -> `Prompt Logic`) 검증 (Pass)

### Known Issues
- 현재 `analyze_failure`는 Rule-based로 동작하며, 추후 LLM 기반의 심층 분석으로 확장이 필요합니다.
