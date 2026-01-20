# 🚀 Rag Ingestion: Purpose-Driven Knowledge Graph Engine

> **"지식의 재구조화"**: 단순 수집을 넘어, 아이디어를 구체화(Exploration to Structuring)하는 **지능형 지식 공장**입니다.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://www.langchain.com/)

---

## 🧠 Philosophy

사용자가 "나 이런 책을 쓰고 싶어" 혹은 "이런 서비스를 벤치마킹하고 싶어"라고 한마디만 던져도, 시스템은 다음과 같이 움직입니다.

1.  **발산 (Divergence)**: 관련 소스(유튜브, 블로그, 도서)를 샅샅이 뒤져 데이터를 수집합니다.
2.  **연결 (Connection)**: 데이터 간의 논리적 모순, 보완, 발전 관계를 찾아 연결합니다.
3.  **수렴 (Convergence)**: 수집된 정보를 '책의 목차'나 '전략 보고서' 형태로 재구성하여 제안합니다.

---

## 🏗️ Architecture & Storage Strategy

본 프로젝트는 **Clean Architecture**와 **DDD(Domain-Driven Design)** 원칙을 따릅니다. 상세 내용은 [Architecture Guide](docs/architecture/architecture.md)를 참고하세요.

### 3-Layer Storage Strategy
데이터를 3가지 레이어로 나누어 저장함으로써 다각적인 분석을 가능하게 합니다.

#### 1. Atomic Layer (기초 사실)
*   **목적**: 데이터의 원본 무결성과 출처 보존
*   **저장소**: **Neo4j** (Metadata/Relation) + **ChromaDB** (Vector/Content)
*   **구성**: `Source`, `Document`, `Chunk`

#### 2. Semantic Layer (의미 추출)
*   **목적**: 텍스트에서 의미 있는 개체(Entity)와 속성 추출
*   **기술**: LLM (Gemini 2.0 Flash) 기반 추출 파이프라인
*   **구성**:
    *   **Entities**: `Person`, `Organization`, `Technology`, `Concept`, `Location`, `Event`, `Activity`
    *   **Metadata**: Title, Summary, Keywords

#### 3. Knowledge Layer (지식 연결)
*   **목적**: 개체 간의 관계와 논리적 맥락 연결 (Knowledge Graph)
*   **구성**:
    *   **Relationships**: `MENTIONS`, `WORKS_FOR`, `FOUNDED`, `USES`, `RELATED_TO`, `PERFORMED`, `SUPPORTS`
    *   **Graph RAG**: 그래프 기반 복합 추론 지원

---

## 📚 Documentation

시스템에 대한 상세한 문서는 `docs/` 디렉토리에서 확인할 수 있습니다.

### 🏛 Architecture
*   [**Clean Architecture**](docs/architecture/architecture.md): 시스템 설계 원칙 및 계층 구조
*   [**Ontology Design**](docs/architecture/ontology.md): Entity 및 Relationship 정의
*   [**Tech Stack**](docs/architecture/tech_stack.md): 기술 선정 배경 (FastAPI, Neo4j, LangChain 등)

### 📖 Guides
*   [**Getting Started**](docs/guides/admin_guide.md): 설치 및 실행 가이드
*   [**Async Processing**](docs/guides/async_guide.md): 비동기 수집 파이프라인 구조
*   [**Testing Strategy**](docs/guides/testing_strategy.md): TDD/BDD 테스트 접근 방식

### ✨ Features
*   [**LangGraph Backtracking**](docs/features/langgraph_backtracking.md): 지능형 재시도 및 에러 복구 전략

---

## 🏃 Quick Start

### 1. 실행 (Docker)
```bash
# 전체 스택 실행 (Backend, Admin, DBs)
docker compose up --build

# 종료
docker compose down
```

### 2. 주요 엔드포인트
| 서비스 | URL | 설명 |
| :--- | :--- | :--- |
| **Admin Dashboard** | [http://localhost:8501](http://localhost:8501) | 작업 모니터링 및 제어 |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI |
| **Neo4j Browser** | [http://localhost:7474](http://localhost:7474) | 그래프 데이터 탐색 (ID/PW: neo4j/password) |

---

## 🗺 Roadmap

현재 프로젝트는 **Phase 5**까지 완료되었으며, 지식 그래프 구축 및 워크플로우 자동화를 향해 나아가고 있습니다. 자세한 계획은 [Backlog](backlog/queue.md)를 참고하세요.

*   [x] **Phase 1**: Functional Foundation (Scraper, Hybrid Storage)
*   [x] **Phase 2**: Observability (Admin Dash, Async Jobs)
*   [x] **Phase 3**: Intelligence (Semantic Extraction, Ontology)
*   [x] **Phase 4**: Graph Construction (Entity Nodes, Relationships)
*   [ ] **Phase 5**: Knowledge Reasoning (Logic Resolver, Graph RAG) 🚧 *In Progress*

> **Note for AI Agents**: 코드를 구현할 때는 `agent.md`의 규칙을 준수하고, 저장소 계층 구조(Composite Storage)를 유지해야 합니다.
