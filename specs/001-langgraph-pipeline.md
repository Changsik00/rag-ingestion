# Spec: 001 - LangGraph Pipeline Setup

## 1. Goal
Rag Ingestion의 핵심 엔진인 **LangGraph 기반 데이터 수집 파이프라인**의 기초 구조를 수립합니다.
확장 가능한 상태 관리(State Management)와 기본 노드/엣지 흐름을 정의하는 것이 목표입니다.

## 2. In Scope
- **Domain Modeling**: `Source` (수집 대상 데이터)에 대한 Pydantic 모델 정의.
- **State Definition**: LangGraph의 `GraphState` 정의 (수집된 데이터 리스트, 에러 로그 등).
- **Core Graph Construction**:
    - `Workflow` 클래스 생성.
    - Dummy Nodes (`fetch_source`, `extract_content`) 구현 (인터페이스 정의 위주).
    - Basic Edge 연결.
- **Configuration**: 파이프라인 실행을 위한 기본 설정 관리.

## 3. Out of Scope
- 실제 YouTube/Web Scraper 구현 (EPIC-02에서 진행)
- Neo4j, LLM 연동 로직 구현 (EPIC-03, 04에서 진행)

## 4. Technical Design

### 4.1 Architecture (Clean Architecture)
```
src/
├── domain/
│   ├── models/
│   │   └── source.py       # Entity: Source, Chunk
│   └── state.py            # LangGraph State Definition
├── application/
│   ├── workflow.py         # Graph Construction Logic
│   └── nodes/
│       ├── __init__.py
│       └── base.py         # Abstract Base Classes for Nodes
└── main.py                 # Entry Point
```

### 4.2 State Schema
```python
class GraphState(TypedDict):
    urls: List[str]            # 입력 URL 목록
    sources: List[Source]      # 수집/가공된 Source 객체들
    errors: List[str]          # 에러 로그
    status: str                # 진행 상태
```

### 4.3 Data Model (Proto)
```python
class Source(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: HttpUrl
    title: Optional[str] = None
    raw_content: Optional[str] = None
    chunks: List[Chunk] = []
    metadata: Dict[str, Any] = {}
```

## 5. Verification Plan
- **Unit Tests**:
    - `Source` 모델 유효성 검사 테스트.
    - `Workflow` 그래프 생성 및 컴파일 테스트.
    - Dummy Node를 통과했을 때 State 변화 검증.
- **Integration Test**:
    - 실제로 그래프를 실행(`invoke`)하여 에러 없이 종료되는지 확인.
