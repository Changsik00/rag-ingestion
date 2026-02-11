# refactor(spec-076): refined RAG 3-layer architecture

## 📋 Summary

### 배경 및 목적
기존의 RAG 3계층 구조를 더 체계적인 계층형 경로로 재구성하고, Chat과 Ingest 유스케이스 간의 핵심 자산 공유를 용이하게 하기 위해 리팩토링을 수행했습니다. 주요 계층(Brain, Retrieval, Orchestration)의 용어를 정립하고, RAG 전용 중간 폴더를 제거하여 구조를 최적화했습니다.

### 주요 변경 사항
- [x] **Domain Layer Refinement**: Brain 및 Retrieval을 위한 공통 인터페이스(`IBrainService`, `IReranker`, `IRetrievalService`) 정의. `text_cleaner.py`를 `app/core/`로 이동하여 공용화.
- [x] **Infrastructure Hierarchical Pathing**: 
  - `app/infrastructure/brain/`: 의도 분류, 리랭킹, 답변 생성 구현체 이동.
  - `app/infrastructure/retrieval/`: 하이브리드 검색 구현체 이동.
- [x] **Orchestration Layer Specialization**: 
  - `ChatOrchestrator`: 대화형 RAG을 위한 전용 서비스 구현.
  - `IngestOrchestrator`: 메타데이터 추출 및 인제션 워크플로우 전용 서비스 구현.
- [x] **AI Infra Separation**: LangGraph 빌더 및 노드를 `chat`과 `ingest` 경로로 분리(`app/infrastructure/ai/chat/`, `app/infrastructure/ai/ingest/`).
- [x] **Dependency Injection**: 새로운 계층 구조 및 오케스트레이터에 맞춰 `dependencies.py` 및 MCP 서버 업데이트.
- [x] **Cleanup**: 더 이상 사용되지 않는 레거시 `rag` 중간 디렉토리 및 레거시 파일 제거.

## 🎯 Key Review Points
1. **Tiered Service Structure**: Brain(인프라), Retrieval(인프라), Orchestration(애플리케이션) 간의 명확한 책임 분리.
2. **Interface-based Injection**: 구체적인 구현체 대신 도메인 인터페이스를 사용하여 유연성 확보.
3. **Use-case Orchestrators**: Chat과 Ingest 워크플로우가 각각의 전용 오케스트레이터를 통해 독립적으로 관리되는 구조.

## 🧪 Verification

### Automated Tests
```bash
# Orchestration Layer Test
uv run pytest tests/application/services/orchestration/test_chat_service.py

# Infrastructure Layer Tests
uv run pytest tests/infrastructure/retrieval/test_retrieval_service.py
uv run pytest tests/unit/infrastructure/brain/

# Core Utility Test
uv run pytest tests/unit/core/test_text_cleaner.py
```
**테스트 결과 요약:**
- ✅ `ChatOrchestrator` 파이프라인 및 폴백 로직 검증 완료
- ✅ `RetrievalService` 계층 이동 후 검색 기능 검증 완료
- ✅ `Brain` 레이어(Service, Reranker, Generator) 유닛 테스트 통과
- ✅ `text_cleaner` 핵심 유틸리티 테스트 통과

## 📦 Files Changed (Major)

### 🆕 New/Moved Paths
- `app/domain/interfaces/`: `brain.py`, `retrieval.py` (Common protocols)
- `app/infrastructure/brain/`: `service.py`, `reranker.py`, `answer_generator.py`
- `app/infrastructure/retrieval/`: `service.py`
- `app/application/services/orchestration/`: `chat.py`, `ingest.py`
- `app/infrastructure/ai/chat/`, `app/infrastructure/ai/ingest/`: Graph builders and nodes

### 🛠 Updated Files
- `app/interfaces/api/dependencies.py`: Refined DI wiring
- `app/interfaces/mcp/server.py`: Integrated with `ChatOrchestrator`
- `app/infrastructure/repositories/chroma.py`: Bug fixes and linting alignment

## ✅ Definition of Done
- [x] 모든 핵심 단위/통합 테스트 통과
- [x] `walkthrough.md` 업데이트 완료
- [x] 레거시 RAG 디렉토리 완전 삭제
- [x] Ruff lint 및 format 무결성 확인
