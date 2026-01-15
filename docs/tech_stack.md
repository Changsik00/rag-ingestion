# Technology Stack & Decision Records

이 문서는 프로젝트에서 사용하는 핵심 기술 스택과 그 선정 이유를 기록합니다.

## 1. Core Language & Environment
- **Python**: 3.10+ (최신 안정 버전)
- **Package Manager**: **`uv`**
    - **Selection Reason**: 
        - Rust 기반으로 작성되어 `Poetry`나 `pip` 대비 압도적인 속도를 제공합니다.
        - 가상환경 관리(`venv`)와 패키지 리졸빙을 통합적으로 처리하여 개발 경험(DX)이 우수합니다.
        - 최신 Python 생태계에서 가장 빠르게 성장하고 있는 표준 도구입니다.

## 2. Web Framework
- **FastAPI**
    - **Selection Reason**:
        - `LangGraph`와의 호환성이 뛰어나며, 비동기(`async`/`await`) 처리에 최적화되어 있습니다.
        - 추후 MCP(Model Context Protocol) 서버로 확장 시, 표준 인터페이스 구현이 가장 용이합니다.

## 3. Data Modeling
- **Pydantic v2**
    - **Selection Reason**:
        - Rust 코어 기반으로 v1 대비 유효성 검사 속도가 비약적으로 향상되었습니다.
        - **Why not SQLModel?**: 
            - 본 프로젝트는 `Neo4j`(Graph DB)와 `ChromaDB`(Vector DB)를 주 저장소로 사용합니다.
            - `SQLModel`은 `SQLAlchemy`를 내장하여 SQL DB에 최적화된 ORM이므로, Graph DB 중심 프로젝트에는 불필요한 의존성입니다.
            - 가볍고 빠른 `Pydantic`만으로 도메인 모델을 정의하는 것이 클린 아키텍처 원칙(의존성 최소화)에 부합합니다.

## 4. Pipeline & Logic
- **LangGraph**: 상태 기반(State-based)의 복잡한 에이전트 워크플로우 제어.
- **Neo4j**: 지식 간의 관계(Onotology)를 저장하고 탐색.
