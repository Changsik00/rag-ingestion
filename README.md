# 🚀 Rag Ingestion: Purpose-Driven Knowledge Graph Engine

`Rag Ingestion`은 단순한 데이터 수집기가 아닙니다. 이 프로젝트는 **사용자의 아이디어가 구체화되는 과정(Exploration to Structuring)**을 지원하며, `Rag Planner`가 창의적인 기획을 할 수 있도록 **다각도로 해석된 지식**을 공급하는 "지능형 지식 공장"입니다.

---

## 🧠 프로젝트 철학: "지식의 재구조화"

> **Tech Stack Info**: 이 프로젝트는 `uv`, `FastAPI`, `Pydantic v2`를 기반으로 구축되었습니다. 상세한 기술 선정 배경은 [docs/tech_stack.md](docs/tech_stack.md)를 참고하세요.

사용자가 "나 이런 책을 쓰고 싶어" 혹은 "이런 서비스를 벤치마킹하고 싶어"라고 한마디만 던져도, 시스템은 다음과 같이 움직입니다.

1. **발산(Divergence):** 관련 소스(유튜브, 블로그, 도서)를 샅샅이 뒤져 데이터를 긁어옵니다.
    
2. **연결(Connection):** 데이터들 사이의 논리적 모순, 보완, 발전 관계를 찾아 선을 잇습니다.
    
3. **수렴(Convergence):** 수집된 정보를 '책의 목차'나 '전략 보고서의 항목'으로 재구성하여 사용자에게 제안합니다.
    

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

## 📂 상세 온톨로지 전략 (Detailed Ontology Strategy)

이 프로젝트의 핵심은 데이터를 **3가지 레이어**로 동시에 저장하여, 하나의 데이터를 여러 관점에서 바라보게 하는 것입니다.

### 1. Atomic Layer (기초 사실 정보)

- **목적:** 데이터의 무결성과 출처를 보존합니다.
    
- **엔티티:** `Source`(URL, Title), `Author`, `Concept`(핵심 용어), `Chunk`(원문 조각).
    
- **관계:** `WRITTEN_BY`, `PUBLISHED_AT`, `MENTIONS`.
    

### 2. Intent-Driven Layer (목적 기반 재구성)

- **목적:** 사용자가 선택한 프로젝트 성격에 따라 데이터의 역할을 정의합니다.
    
- **프로젝트별 확장:**
    
    - **Book Writing Mode:** `Chapter`(목차), `Anecdote`(사례), `Hook`(관심 유발 요소), `Narrative_Arc`.
        
    - **Strategy Planning Mode:** `Competitor`(경쟁사), `Feature`(기능), `Advantage`(강점), `Pricing_Model`.
        
    - **PPT/Presentation Mode:** `Key_Message`(핵심 요약), `Visual_Idea`(도식화 아이디어), `Statistics`(통계 수치).
        

### 3. Insight & Logic Layer (논리적 연결)

- **목적:** 단순 정보의 나열이 아닌 '비판적 사고'를 가능하게 합니다.
    
- **관계 속성:**
    
    - `CONTRADICTS`: A 자료와 B 자료의 주장이 상충될 때 (예: "RAG가 최고다" vs "RAG는 비용이 비싸다").
        
    - `SUPPLEMENTS`: 정보가 서로 보완될 때.
        
    - `EVOLVED_FROM`: 기술이나 아이디어의 발전 계보를 나타낼 때.
        

---

## 🤖 에이전트 작동 원리 (Agent Reasoning Logic)

`agent.md`가 참조할 핵심 로직입니다.

1. **동적 스키마 생성:** 사용자의 "화두"를 받으면, LLM은 해당 도메인에 맞는 `Dynamic Schema`를 먼저 설계합니다. (예: "건강 관련 책" -> '영양소', '운동법', '식단' 엔티티 활성화)
    
2. **Incremental Batch Ingestion:** * 대량 수집 시 기존 DB의 노드들과 **Hash 값을 비교**하여 새로운 정보만 인제스션합니다.
    
    - 기존 노드와 유사도가 90% 이상인 경우 '업데이트'하고, 새로운 관점인 경우 '연결'합니다.
        
3. **Multi-Model Choice:**
    
    - **Extraction:** 컨텍스트가 긴 자료(유튜브 스크립트 등)는 `Gemini 1.5 Flash`를 사용합니다.
        
    - **Refining/Logic:** 추출된 지식들 간의 모순을 검증하고 마인드맵 구조를 짤 때는 `GPT-4o`나 `Claude 3.5 Sonnet`을 선택적으로 호출합니다.
        

---

## 🗺 마인드맵 및 시각화 지원

`Rag Planner`가 시각적으로 아이디어를 확장할 수 있도록, 지식 그래프를 **Tree 구조**로 변환하여 제공합니다.

- **Clustering API:** 수집된 수백 개의 노드를 시맨틱 유사도에 따라 5~7개의 핵심 가지(Branch)로 묶어줍니다.
    
- **Hierarchy Generation:** 중심 아이디어로부터 파생되는 부모-자식 관계를 설정하여 JSON 형태로 반환합니다.
    

---

## 🛠 기술적 상세 (Technical Details)

### 1. 하이브리드 저장소 운영

- **Neo4j:** Cypher 쿼리를 통해 복잡한 관계(Relationship)를 탐색합니다. `Rag Planner`가 "A와 B의 차이점이 뭐야?"라고 물을 때 이 그래프를 훑습니다.
    
- **ChromaDB:** 각 노드에 대응하는 상세 텍스트 원문을 벡터로 저장하여, 필요할 때 '날것의 정보'를 빠르게 가져옵니다.
    

### 2. 배치 및 업데이트 정책

- **Sync Mode:** 사용자와 대화 중에 실시간으로 소량 수집.
    
- **Batch Mode:** 지정된 링크 리스트를 백그라운드에서 한꺼번에 처리하고 작업 완료 알림.
    

---

## 🚀 프로젝트 로드맵

1. **Phase 1: Foundation** - LangGraph 기반의 기본 수집-추출 파이프라인 구축.
    
2. **Phase 2: Ontology** - 3대 프로젝트 모드(책, 전략, PPT) 전용 온톨로지 스키마 확립.
    
3. **Phase 3: Intelligence** - 데이터 간 모순 검증 및 계층적 마인드맵 변환 엔진 개발.
    
4. **Phase 4: Integration** - `Rag Planner`와 MCP 기반 실시간 지식 공유 연동.
    

---

> **Note for AI Agents:** 이 문서는 프로젝트의 상위 설계도입니다. 코드를 구현할 때는 `agent.md`의 세부 지침을 따르되, 데이터 저장 시 반드시 **다층 온톨로지(Multi-layer)** 원칙을 준수해야 합니다.

