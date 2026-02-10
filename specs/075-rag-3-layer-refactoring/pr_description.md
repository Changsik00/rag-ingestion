# refactor(spec-075): implementation of RAG 3-layer architecture

## 📋 Summary

### 배경 및 목적
기존의 `RAGNodes`에 집중되어 있던 비대하고 복잡한 로직을 Clean Architecture 원칙에 따라 3계층(Brain, Retrieval, Orchestration)으로 분리하여 유지보수성, 테스트 가능성 및 확장성을 개선합니다.

### 주요 변경 사항
- [x] **Brain Layer**: 의도 분류(`BrainService`), 리랭킹(`Reranker`), 답변 생성(`AnswerGenerator`) 로직을 도메인 레이어로 이동 및 캡슐화.
- [x] **Retrieval Layer**: 하이브리드 검색 로직을 `RetrievalService`로 독립시키고, 텍스트 정제 로직(`text_cleaner.py`)을 공통화.
- [x] **Orchestration Layer**: 각 레이어를 조율하고 비즈니스 흐름을 관리하는 `RAGOrchestrator` 구현.
- [x] **LangGraph Integration**: `RAGGraphBuilder`가 `RAGOrchestrator`를 사용하도록 리팩토링하여 그래프 노드와 실제 로직을 분리.
- [x] **Dependency Injection**: 새로운 레이어 구조에 맞춰 `dependencies.py` 의존성 주입 설정 업데이트.
- [x] **Cleanup**: 더 이상 사용되지 않는 `RAGNodes` 클래스 및 관련 레거시 코드 제거.

## 🎯 Key Review Points
1. **RAGOrchestrator**: LangGraph 노드에서 비즈니스 로직을 완전히 추출하여 `Orchestrator`에 위임한 구조.
2. **Layer Separation**: Brain(도메인), Retrieval(인프라), Orchestration(애플리케이션) 계층 간의 의존성 흐름.
3. **State Management**: `RAGGraphState`가 각 레이어를 거치며 어떻게 업데이트되는지 확인.

## 🧪 Verification

### Automated Tests
```bash
# Unit Tests for each layer
uv run pytest tests/unit/domain/rag/brain/
uv run pytest tests/infrastructure/rag/retrieval/test_service.py
uv run pytest tests/unit/domain/rag/test_text_cleaner.py

# Integration Test for Graph Wiring
uv run pytest tests/integration/rag/test_rag_graph_wiring.py
uv run pytest tests/integration/scenarios/test_rag_mocked_flow.py
```
**테스트 결과 요약:**
- ✅ `BrainService`, `Reranker`, `AnswerGenerator` 유닛 테스트 통과
- ✅ `RetrievalService` 하이브리드 검색 유닛 테스트 통과
- ✅ `RAGOrchestrator` 조율 로직 통합 테스트 통과
- ✅ LangGraph 노드 및 상태 전이 통합 테스트 통과

### Manual Verification (Scenarios)
1. **End-to-End Wiring**: `RAG` 서비스를 통해 질문을 던졌을 때, 의도 분류 -> 검색 -> 리랭킹 -> 답변 생성 과정이 정상적으로 순회됨을 확인.

## 📦 Files Changed

### 🆕 New Files
- `app/domain/rag/brain/service.py`: 의도 분류 및 쿼리 재작성
- `app/domain/rag/brain/reranker.py`: 도메인 기반 리랭킹 로직
- `app/domain/rag/brain/answer_generator.py`: LLM 답변 생성 및 인용 파싱
- `app/domain/rag/text_cleaner.py`: 텍스트 정제 유틸리티
- `app/application/rag/orchestration/service.py`: 3계층 총괄 오케스트레이터
- `tests/integration/rag/test_rag_graph_wiring.py`: 그래프 연결성 테스트

### 🛠 Modified Files
- `app/infrastructure/ai/rag_graph.py`: Orchestrator 기반으로 그래프 빌더 교체
- `app/infrastructure/rag/retrieval/service.py`: 검색 전용으로 축소 및 정제 로직 위임
- `app/interfaces/api/dependencies.py`: 3계층 기반 DI 설정 업데이트
- `app/interfaces/mcp/server.py`: 레거시 `RAGNodes` 의존성 제거

**Total:** 17 files changed (Refactored codebase)

## ✅ Definition of Done
- [x] 모든 단위/통합 테스트 통과
- [x] `walkthrough.md` 작성 및 아카이브 완료
- [x] `pr_description.md` 작성 및 아카이브 완료
- [x] Ruff lint 및 format 확인 완료
