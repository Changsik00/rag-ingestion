# Plan: LangGraph Pipeline Setup

Ref: [Spec](file:///Users/ck/Project/doit/rag-ingestion/specs/001-langgraph-pipeline.md)

## 1. 목표 (Goal)
데이터 수집 파이프라인의 핵심인 LangGraph 아키텍처 기초를 수립합니다.
도메인 모델(`Source`), 상태(`GraphState`), 그리고 기본적인 워크플로우(`Workflow`) 구조를 구현합니다.

## 2. 사용자 검토 필요 사항 (User Review Required)
- **Dummy Node 사용**: 실제 크롤링 로직 대신 더미 노드를 사용하여, 전체적인 파이프라인 흐름(Flow)과 상태 전이(State Transition)가 정상 작동하는지 검증하는 데 집중합니다.

## 3. 변경 예정 사항 (Proposed Changes)

### Domain Layer
#### [NEW] [source.py](file:///Users/ck/Project/doit/rag-ingestion/src/domain/models/source.py)
- `Source`, `Chunk` Pydantic 모델 정의.
- 주요 필드: `id`, `url`, `raw_content`, `chunks`.

#### [NEW] [state.py](file:///Users/ck/Project/doit/rag-ingestion/src/domain/state.py)
- `GraphState` TypedDict 정의.
- 포함 항목: `urls`, `sources`, `errors`, `status`.

### Application Layer
#### [NEW] [base.py](file:///Users/ck/Project/doit/rag-ingestion/src/application/nodes/base.py)
- 노드(Node) 구현을 위한 추상 기본 클래스(ABC) 정의.

#### [NEW] [mock_nodes.py](file:///Users/ck/Project/doit/rag-ingestion/src/application/nodes/mock_nodes.py)
- `fetch_source_node`: URL 입력 -> 더미 콘텐츠가 포함된 Source 반환.
- `extract_content_node`: Source 입력 -> 더미 Chunk가 포함된 Source 반환.

#### [NEW] [workflow.py](file:///Users/ck/Project/doit/rag-ingestion/src/application/workflow.py)
- `StateGraph` 초기화 (`GraphState` 사용).
- 노드 추가 및 엣지 연결: `fetch` -> `extract` -> `END`.
- 그래프 컴파일 (`compile()`).

### Entry Point
#### [NEW] [main.py](file:///Users/ck/Project/doit/rag-ingestion/src/main.py)
- 테스트 URL로 그래프를 `invoke`하고 결과를 출력하는 간단한 CLI 실행 파일.

## 4. 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Tests)
- **단위 테스트 (Unit Tests)**: `pytest tests/unit/test_workflow.py`
    - `Source` 모델 유효성 검증.
    - `GraphState` 구조 검증.
    - 그래프 컴파일 테스트 (끊긴 엣지 확인).

- **통합 테스트 (Integration Test)**: `pytest tests/integration/test_pipeline_execution.py`
    - `workflow.invoke({"urls": ["http://test.com"]})` 실행.
    - 최종 상태(State)에 처리된 `Source`가 존재하는지 검증.

### 수동 검증 (Manual Verification)
- `python src/main.py` 실행 후 콘솔 출력을 통해 그래프 실행 경로(Path) 확인.
