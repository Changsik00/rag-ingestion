# Product Backlog

이 문서는 `Rag Ingestion` 프로젝트의 전체 기능 목록과 개발 로드맵을 관리합니다.
`README.md`의 로드맵을 기반으로 초기 항목을 구성했습니다.

## 📅 Roadmap Overview

| Phase | Focus | Description | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Foundation** | LangGraph 기반 기본 수집-추출 파이프라인 | 🟡 Ready |
| **Phase 2** | **Ontology** | 3대 모드(책, 전략, PPT) 전용 온톨로지 스키마 | ⚪️ Pending |
| **Phase 3** | **Intelligence** | 모순 검증 및 계층적 마인드맵 변환 엔진 | ⚪️ Pending |
| **Phase 4** | **Integration** | Rag Planner 및 MCP 연동 | ⚪️ Pending |

---

## 📝 Detailed Backlog Items

### Phase 1: Foundation (Current Priority)
기본적인 데이터 수집 및 'Atomic Layer' 구축에 집중합니다.

- [ ] **[EPIC-01] LangGraph Pipeline Setup**
    - [ ] Basic Graph Structure 정의 (State, Nodes, Edges)
    - [ ] `Source` 데이터 모델 정의 (Pydantic)
- [ ] **[EPIC-02] Data Ingestion Adapters**
    - [ ] YouTube Transcript Scraper
    - [ ] Web Page Text Extractor
- [ ] **[EPIC-03] Neo4j Integration (Atomic Layer)**
    - [ ] Neo4j Docker Compose 설정
    - [ ] Basic Cypher Query (Create/Merge Nodes) 구현
- [ ] **[EPIC-04] LLM Extraction Node**
    - [ ] Gemini 1.5 Flash 연동 (Long Context Extraction)

### Phase 2: Ontology
목적 기반의 'Intent-Driven Layer'를 구현합니다.

- [ ] **[EPIC-05] Book Writing Schema**
    - [ ] `Anecdote`, `Hook` 엔티티 정의 및 추출 프롬프트
- [ ] **[EPIC-06] Strategy Planning Schema**
    - [ ] `Competitor`, `Pricing_Model` 엔티티 정의
- [ ] **[EPIC-07] PPT Schema**
    - [ ] `Key_Message`, `Visual_Idea` 엔티티 정의

### Phase 3: Intelligence
'Insight & Logic Layer'와 분석 기능을 구현합니다.

- [ ] **[EPIC-08] Logic Relationship Analysis**
    - [ ] `CONTRADICTS`, `SUPPLEMENTS` 관계 분석 로직 (GPT-4o/Sonnet)
- [ ] **[EPIC-09] Tree Hierarchy Generation**
    - [ ] Knowledge Graph to Tree 변환 알고리즘

### Phase 4: Integration
외부 서비스 연동을 진행합니다.

- [ ] **[EPIC-10] MCP Server Implementation**
    - [ ] Rag Planner용 툴 노출
- [ ] **[EPIC-11] Background Batch Processor**
    - [ ] 비동기 대량 수집 처리기
