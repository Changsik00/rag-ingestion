# 🚀 Feature: LangGraph Pipeline Skeleton (Spec-001)

## 1. ✨ Summary
**Rag Ingestion** 프로젝트의 심장부인 `LangGraph` 기반 데이터 수집 파이프라인의 **기초 아키텍처**를 구축했습니다.
복잡한 로직 없이 **데이터의 흐름(Flow)**과 **상태 관리(State Management)**가 정상적으로 작동하는지 확인하는 것이 목표입니다.

## 2. 🏗️ Architecture & Changes

이번 PR은 **Clean Architecture** 원칙에 따라 3가지 레이어로 구성되었습니다.

### 🟡 Domain Layer (순수 로직)
- **`Source` & `Chunk` Model** (`src/domain/models/source.py`):
    - 수집된 데이터(`Source`)와 분할된 텍스트(`Chunk`)를 담는 그릇입니다.
    - `Pydantic v2`를 사용하여 타입 안전성을 보장합니다.
- **`GraphState`** (`src/domain/state.py`):
    - 파이프라인 전체를 관통하는 **상태(Context)** 정의입니다. (`urls`, `sources`, `status`)

### 🟢 Application Layer (비즈니스 흐름)
- **`Mock Nodes`** (`src/application/nodes/mock_nodes.py`):
    - 실제 크롤링 대신 더미 데이터를 생성하는 노드들입니다. (추후 실제 로직으로 교체될 예정)
- **`Workflow`** (`src/application/workflow.py`):
    - `fetch` -> `extract` -> `END`로 이어지는 **LangGraph**를 조립합니다.

### 🔵 Entry Point (실행 진입점)
- **`src/main.py`**:
    - CLI에서 파이프라인을 직접 실행해볼 수 있는 진입점입니다.

---

## 3. 🔍 How it Works (작동 원리)

1.  **Input**: 사용자(혹은 CLI)가 `input_urls` 리스트를 주입합니다.
2.  **Fetch Node**: URL을 받아 `Source` 객체를 생성하고 `raw_content`에 더미 텍스트를 채웁니다.
3.  **Extract Node**: `raw_content`를 읽어 여러 개의 `Chunk` 객체로 분할합니다.
4.  **Output**: 최종적으로 `status: extracted` 상태와 함께 처리된 `Source` 리스트를 반환합니다.

## 4. 👀 Key Review Points

리뷰어 분들은 다음 사항을 중점적으로 봐주세요!

- [ ] **State Schema**: `GraphState`에 정의된 필드(`urls`, `sources`)가 확장성 있어 보이나요?
- [ ] **Pydantic Model**: `Source` 모델의 필드 구성(`id`, `metadata`)이 적절한가요?
- [ ] **Graph Flow**: `Workflow`에서 노드 연결 순서가 논리적인가요?
- [ ] **Structure**: 파일들이 `domain` vs `application` 폴더 규칙에 맞게 잘 나뉘었나요?

## 5. ✅ Verification (검증 결과)

모든 테스트가 **Pass** 했습니다.

- **Unit Tests**:
    - `uv run pytest tests/unit` 👉 **Passed** (4 tests)
- **Integration Tests**:
    - `uv run pytest tests/integration` 👉 **Passed** (1 test)
- **Manual Check**:
    - `uv run python -m src.main` 👉 **Success** (Output verified)
