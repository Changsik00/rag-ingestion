# 🚀 Rag Ingestion: Purpose-Driven Knowledge Graph Engine

`Rag Ingestion`은 **아이디어를 구체화하는 과정(Exploration to Structuring)**을 지원하며, `Rag Planner`가 창의적인 기획을 할 수 있도록 **다각도로 해석된 지식**을 공급하는 \"지능형 지식 공장\"입니다.

> **Tech Stack**: 이 프로젝트는 `uv`, `FastAPI`, `Pydantic v2`, `LangChain`, `Neo4j`, `ChromaDB`를 기반으로 구축되었습니다. 상세한 기술 선정 배경은 [docs/tech_stack.md](docs/tech_stack.md)를 참고하세요.

---

## 🎯 현재 구현 상태 (Current Status)

### ✅ Phase 1: The Functional Foundation (완료)
- **Spec 001**: FastAPI 서버 + Web Scraper (`POST /ingest/web`)
- **Spec 002**: Neo4j + ChromaDB 하이브리드 저장소

### ✅ Phase 2: Observability & Scalability (완료)
- **Spec 003**: Streamlit Admin Dashboard (Job 모니터링 & 재시도)
- **Spec 004**: 비동기 백그라운드 작업 처리 (Async Ingestion)

### ✅ Phase 3: Progressive Intelligence (진행 중)
- **Spec 005**: ✅ **Semantic Extraction** - Gemini 2.0 Flash를 활용한 메타데이터 추출
  - Title, Summary, Keywords, Entities 구조화
  - LangChain 기반 Extraction Pipeline
- **Spec 006**: ✅ **Clean Architecture Refactoring** - Domain 격리 및 확장성 개선
  - Python Protocol을 활용한 LLM 인터페이스 추상화
  - Infrastructure Adapter 패턴 적용
- **Spec 007-008**: 🚧 **Ontology & Knowledge Graph** (예정)

---

## 🏃 Quick Start & Service Ports

개발 및 운영을 위한 빠른 실행 가이드입니다. 더 자세한 내용은 [docs/admin_guide.md](docs/admin_guide.md)를 참고하세요.

### 1. 실행 명령어
```bash
# 전체 스택 실행 (Backend, Admin, DBs)
docker compose up --build

# 전체 종료 및 정리
docker compose down
```

### 2. 서비스 포트 (Service Endpoints)
| 서비스 (Service) | 포트 (Port) | 접속 주소 (URL) | 설명 |
| :--- | :--- | :--- | :--- |
| **Admin Dashboard** | `8501` | [http://localhost:8501](http://localhost:8501) | 작업 상태 모니터링 및 제어 |
| **Backend API** | `8000` | [http://localhost:8000/docs](http://localhost:8000/docs) | REST API 문서 (Swagger UI) |
| **Neo4j** | `7474` | [http://localhost:7474](http://localhost:7474) | 그래프 DB 브라우저 (ID/PW: neo4j/password) |

---

## 🧠 프로젝트 철학: \"지식의 재구조화\"

사용자가 \"나 이런 책을 쓰고 싶어\" 혹은 \"이런 서비스를 벤치마킹하고 싶어\"라고 한마디만 던져도, 시스템은 다음과 같이 움직입니다.

1. **발산(Divergence):** 관련 소스(유튜브, 블로그, 도서)를 샅샅이 뒤져 데이터를 긁어옵니다.
    
2. **연결(Connection):** 데이터들 사이의 논리적 모순, 보완, 발전 관계를 찾아 선을 잇습니다.
    
3. **수렴(Convergence):** 수집된 정보를 '책의 목차'나 '전략 보고서의 항목'으로 재구성하여 사용자에게 제안합니다.

---

## 📂 3-Layer 저장 전략 (Storage Architecture)

이 프로젝트의 핵심은 데이터를 **3가지 레이어**로 저장하여, 하나의 데이터를 여러 관점에서 바라보게 하는 것입니다.

### 1. Atomic Layer (기초 사실 정보) - ✅ 구현 완료

- **목적:** 데이터의 무결성과 출처를 보존합니다.
- **엔티티:** `Source`(URL, Title), `Document`(원문), `Chunk`(원문 조각).
- **관계:** `SCRAPED_FROM`, `CREATED_BY`.
- **현재 상태**: Neo4j + ChromaDB 하이브리드 저장 (Spec 002)

### 2. Semantic Layer (의미 추출) - ✅ 기본 구현 완료

- **목적:** 텍스트에서 의미있는 정보를 추출합니다.
- **엔티티:** `Person`, `Organization`, `Technology`, `Topic` (from Entities)
- **속성:** `Title`, `Summary`, `Keywords` (from Metadata)
- **현재 상태**: LLM 기반 추출 완료 (Spec 005-006)

### 3. Intent-Driven Layer (목적 기반 재구성) - 🚧 예정

- **목적:** 사용자가 선택한 프로젝트 성격에 따라 데이터의 역할을 정의합니다.
- **프로젝트별 확장:**
    - **Book Writing Mode:** `Chapter`(목차), `Anecdote`(사례), `Hook`(관심 유발 요소)
    - **Strategy Planning Mode:** `Competitor`(경쟁사), `Feature`(기능), `Advantage`(강점)
    - **PPT/Presentation Mode:** `Key_Message`, `Visual_Idea`, `Statistics`
- **예정 작업**: Spec 007-008에서 구현

### 4. Insight & Logic Layer (논리적 연결) - 🚧 예정

- **목적:** 단순 정보의 나열이 아닌 '비판적 사고'를 가능하게 합니다.
- **관계 속성:**
    - `CONTRADICTS`: A 자료와 B 자료의 주장이 상충될 때
    - `SUPPLEMENTS`: 정보가 서로 보완될 때
    - `EVOLVED_FROM`: 기술이나 아이디어의 발전 계보

---

## 🏗️ Architecture: Clean Architecture + DDD

본 프로젝트는 **Clean Architecture** 원칙을 준수하여 비즈니스 로직을 프레임워크로부터 격리합니다.

### 핵심 원칙
1. **Dependency Rule**: 의존성은 항상 Domain(핵심)을 향한다
2. **Domain Isolation**: 비즈니스 로직은 DB/프레임워크와 독립적
3. **Protocol Pattern**: Python Protocol을 활용한 인터페이스 추상화 (Spec 006)

상세 내용: [docs/architecture.md](docs/architecture.md)

---

## 🤖 LLM 통합 전략 (Current Implementation)

### Spec 005-006: Semantic Extraction Pipeline

1. **LLM Interface 추상화**
   - Python `Protocol`을 활용한 인터페이스 정의
   - Domain은 추상화만 의존, 구현체는 Infrastructure에 위치

2. **Adapter Pattern**
   ```
   Domain (SemanticExtractor)
     → LLMInterface (Protocol)
        ← LangChainAdapter (Infrastructure)
           → Gemini 2.0 Flash
   ```

3. **Extraction Output**
   - **Title**: 문서의 핵심 제목
   - **Summary**: 3문장 요약
   - **Keywords**: 5-10개 핵심 키워드
   - **Entities**: 분류된 개체 (Person, Organization, Technology, Topic)

### Future: Multi-Model Strategy (예정)

- **Extraction**: 컨텍스트가 긴 자료(유튜브 스크립트 등)는 `Gemini 1.5 Flash`
- **Refining/Logic**: 추출된 지식들 간의 모순을 검증할 때는 `GPT-4o` 또는 `Claude 3.5 Sonnet`

---

## 🗺 향후 로드맵 (Future Plans)

### Phase 3: Progressive Intelligence (진행 중)
- ✅ Spec 005: Basic Semantic Extraction (완료)
- ✅ Spec 006: Clean Architecture Refactoring (완료)
- 🚧 Spec 007: Ontology Design
- 🚧 Spec 008: Knowledge Graph Construction

### Phase 4: Workflow & Ecosystem
- **Spec 009**: Logic Resolver - 지식 간 모순 탐지
- **Spec 010**: n8n Workflow Integration - 자동 수집 트리거
- **Spec 011**: MCP Server - Claude/Obsidian 연동

상세 로드맵: [backlog/queue.md](backlog/queue.md)

---

## 🛠 Technical Highlights

### 1. 하이브리드 저장소 운영

- **Neo4j**: Cypher 쿼리를 통해 복잡한 관계(Relationship) 탐색
- **ChromaDB**: 각 노드에 대응하는 텍스트를 벡터로 저장하여 의미 기반 검색 지원

### 2. 배치 및 업데이트 정책

- **Sync Mode**: 사용자와 대화 중에 실시간으로 소량 수집
- **Batch Mode**: 지정된 링크 리스트를 백그라운드에서 한꺼번에 처리 (Spec 004)

### 3. Code Quality

- **Ruff Linter**: Rust 기반 초고속 linting (pycodestyle, pyflakes, isort 통합)
- **TDD**: 모든 기능은 단위 테스트로 검증
- **Clean Architecture**: 의존성 방향 엄격 준수

---

## 📚 Documentation

- **[Architecture](docs/architecture.md)**: Clean Architecture 설계 원칙 및 패턴
- **[Tech Stack](docs/tech_stack.md)**: 기술 선정 이유 및 장단점
- **[Async Guide](docs/async_guide.md)**: 비동기 처리 및 백그라운드 작업
- **[Admin Guide](docs/admin_guide.md)**: 서비스 실행 및 관리
- **[Backlog](backlog/queue.md)**: 프로젝트 로드맵 및 우선순위

---

> **Note for AI Agents**: 이 문서는 프로젝트의 **현재 상태와 비전**을 담고 있습니다. 코드를 구현할 때는 `agent.md`의 세부 지침을 따르되, 데이터 저장 시 **3-Layer 아키텍처** 원칙을 준수해야 합니다. Spec 005-006까지 구현이 완료되었으며, 다음 단계는 **Ontology Design (Spec 007)**입니다.
