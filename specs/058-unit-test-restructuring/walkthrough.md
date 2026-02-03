# Walkthrough: Spec-058 Unit Test Restructuring & Stability Upgrade

## 📋 개요
본 워크쓰루는 `Spec 058`에 따라 진행된 유닛 테스트의 구조적 재편과 깨져 있던 테스트 케이스들의 정상화 결과를 정리합니다.

## 🛠 주요 작업 내용

### 1. 테스트 안정성 복구 (Stability Update)
*   **문제**: `RAGNodes` 인터페이스 변경으로 인해 `RunnableConfig` 인자가 누락되어 7개의 테스트가 실패함.
*   **해결**:
    *   `tests/unit/infrastructure/rag/test_rag_nodes.py`에 `mock_config` 피처를 추가하고 모든 호출부에 주입.
    *   `llm.bind()` 메서드 모킹을 통해 런타임 오류 방지.
    *   `agenerate` 대신 `ainvoke`를 사용하는 최신 구현에 맞춰 테스트 코드의 Assert 로직 수정.
    *   `tests/unit/application/test_rag_nodes_spec044.py` 및 `tests/unit/infrastructure/test_rag_reranker.py` 정합성 수정.

### 2. 테스트 구조 재편 (Restructuring)
*   **원칙**: `app/` 소스 코드 구조를 `tests/unit/` 하위 디렉토리에 1:1로 미러링.
*   **재배치 결과**:
    *   **Infrastructure**: `repositories/`, `factories/`, `scrapers/`, `chunker/`, `rag/`로 세분화.
    *   **Domain**: `entities/`, `services/`, `value_objects/` 폴더 생성 및 파일 이동.
    *   **Application**: `services/` 하위로 유스케이스 테스트 이동.
    *   **Interfaces**: `api/v1/`, `mcp/` 등으로 구조 체계화.

### 3. 코드 품질 관리
*   파일 이동 후 `ruff check --fix` 및 `ruff format`을 실행하여 임포트 경로를 자동 교정하고 스타일을 통일함.

### 4. 테스트 품질 정제 (Audit & Refine)
*   **중복 제거**: `test_rag_nodes_spec044.py` 및 `test_usecases.py`를 각각 상위 테스트 파일로 통합하여 유지보수 포인트 일원화.
*   **안정성 강화**: `SemanticChunker` 테스트 시 실제 임베딩 API 호출을 차단하기 위해 `GoogleGenerativeAIEmbeddings`를 Mocking 처리함.
*   **커버리지 확대**:
    *   RAG 검색 전략(`vector`, `graph`, `hybrid`)에 따른 레포지토리 호출 분기 로직 검증 추가.
    *   `ChunkingConfig` Value Object에 대한 기본값 및 유효성 검사 테스트 추가.
    *   인제스션 파이프라인 중 Chunker 단계의 하드 페일 시나리오 대응 테스트 보완.

## 🧪 검증 결과

### Automated Tests
```bash
uv run pytest tests/unit
```
*   **결과**: **158 passed** (0 failed, 7 fixed)
*   **실행 시간**: 약 7.23초

### Directory Structure Verification
```bash
tree tests/unit -L 3
```
*   `tests/unit/infrastructure/repositories/`: `test_chroma.py`, `test_neo4j_graph.py` 등 확인.
*   `tests/unit/domain/services/`: `test_extractor.py`, `test_query_rewriter.py` 등 확인.
*   `tests/unit/application/services/`: `test_ingestion.py`, `test_file_processor.py` 등 확인.

## 📸 결과 스크린샷 
(필요 시 CLI 출력 결과 복사 가능)
```
tests/unit/
├── application
│   └── services
│       ├── test_agent.py
│       ├── test_agent_clarification.py
│       ├── test_analysis_node.py
│       ├── test_file_processor.py
│       ├── test_ingestion.py
│       ├── test_integrity.py
│       └── test_usecases.py
├── domain
│   ├── entities
│   │   └── test_job.py
│   ├── services
│   │   ├── test_entity_relationship.py
│   │   ├── test_extractor.py
│   │   ├── test_intent_classifier.py
│   │   ├── test_ontology.py
│   │   └── test_query_rewriter.py
│   └── test_exceptions.py
└── infrastructure
    ├── chunker
    ├── factories
    ├── rag
    ├── repositories
    └── scrapers
```
