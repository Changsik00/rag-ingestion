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
*   [**Smart Scraper**](docs/features/ingestion_scraper.md): 멀티소스 콘텐츠 수집 및 정규화
*   [**YouTube Ingestion**](docs/features/ingestion_youtube.md): 자막 및 메타데이터 자동 추출
*   [**Contextual RAG**](docs/features/rag_contextual.md): 문맥 보존형 청킹 및 리트리버
*   [**Graph RAG**](docs/features/rag_graph.md): 지식 그래프 기반 추론 전략
*   [**HITL Workflow**](docs/features/hitl_workflow.md): 인간 개입(Human-in-the-Loop) 피드백 루프
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

현재 프로젝트는 **Phase 4**를 완료하였으며, **Phase 5 (Knowledge Reasoning & Agentic Ecosystem)** 구축을 활발히 진행 중입니다. 자세한 계획은 [Backlog](backlog/queue.md)를 참고하세요.

### 📊 Roadmap Status Overview

| Phase | 목표 (Items) | 상태 | 상세 진행 현황 (Queue 기준) |
| :--- | :--- | :---: | :--- |
| **Phase 1** | **Functional Foundation**<br>(Scraper, Hybrid Storage) | ✅ **완료** | • Spec 001-002 완료<br>• 기본 수집/저장 파이프라인 (Neo4j+Chroma) 구축됨 |
| **Phase 2** | **Observability**<br>(Admin Dash, Async Jobs) | ✅ **완료** | • Spec 003-004 완료<br>• Streamlit 대시보드 및 비동기 작업 관리 시스템 가동 중 |
| **Phase 3** | **Intelligence**<br>(Semantic Extraction, Ontology) | ✅ **완료** | • Spec 005-007 완료<br>• LLM 기반 메타데이터/엔티티 추출 및 온톨로지 설계 적용됨 |
| **Phase 4** | **Graph Construction**<br>(Entity Nodes, Relationships) | ✅ **완료** | • **Spec 010, 016 완료**<br>• 지식 그래프 노드 매핑 및 관계(Relationship) 추출/탐색 기능 구현됨 |
| **Phase 5** | **Knowledge Reasoning**<br>(Logic Resolver, Graph RAG) | ✅ **완료** | • **핵심 구현 완료**: Logic Resolver(Spec 021), Graph RAG Fix(Spec 044), Agentic Workflow(Spec 029)<br>• **고도화 완료**: HITL(Spec 022/041/045), Robustness(Spec 043/049), Hybrid Search(Spec 026) 등 "지능형/자동화" 기능 구현됨 |
| **Phase 6** | **Performance & Scalability**<br>(RAG Precision, Local LLM) | 🚀 **진행 중** | • **목표**: 시스템 응답 속도/처리량 최적화 및 비용 효율화<br>• **계획**: RAG Precision(Spec 055), Local LLM(Spec 056), Semantic Chunking(Spec 057) |

*   [x] **Phase 1**: Functional Foundation (Scraper, Hybrid Storage)
*   [x] **Phase 2**: Observability (Admin Dash, Async Jobs)
*   [x] **Phase 3**: Intelligence (Semantic Extraction, Ontology)
*   [x] **Phase 4**: Graph Construction (Entity Nodes, Relationships)
*   [x] **Phase 5**: Knowledge Reasoning & Agentic Ecosystem (Logic Resolver, Graph RAG)
*   [ ] **Phase 6**: Performance Optimization & Scalability (RAG Precision, Local LLM) 🚧 *In Progress*

> **Note for AI Agents**: 코드를 구현할 때는 `agent.md`의 규칙을 준수하고, 저장소 계층 구조(Composite Storage)를 유지해야 합니다.
