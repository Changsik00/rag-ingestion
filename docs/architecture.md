# Project Architecture

본 프로젝트는 **Clean Architecture** 원칙을 따르는 사용자 정의 폴더 구조를 사용합니다.

## Directory Structure

```plaintext
rag-ingestion/
├── app/
│   ├── core/               # 설정 및 공통 유틸리티
│   │   └── config.py       # .env 로드 및 환경 설정
│   ├── domain/             # (Entity Layer) 순수 비즈니스 로직 및 온톨로지 정의
│   │   ├── models/         # Pydantic 기반 노드/관계 모델
│   │   └── interfaces/     # Scraper, DB 등에 대한 추상 인터페이스
│   ├── infrastructure/     # (Adapter Layer) 외부 도구 구현체
│   │   ├── scrapers/       # Firecrawl, YouTube API 연동
│   │   └── db/             # Neo4j, ChromaDB 클라이언트
│   ├── use_cases/          # (Application Layer) LangGraph 워크플로우 엔진
│   │   └── ingestion.py    # 데이터 수집-추출-저장 시나리오
│   └── interfaces/         # (Driver Layer) 외부 진입점
│       ├── cli.py          # MVP 테스트를 위한 CLI 도구
│       └── api/            # Rag Planner 연동을 위한 FastAPI
├── specs/                  # SDD 명세서 저장 (Spec-001, 002...)
├── plans/                  # 실행 계획서 저장 (Plan-001, 002...)
├── tests/                  # TDD를 위한 테스트 코드
├── agent.md                # 에이전트 행동 지침
├── constitution.md         # 프로젝트 불변 법칙
├── pyproject.toml          # uv 기반 의존성 관리
└── README.md
```

## Layer Description

1.  **Domain (Core)**
    *   외부 의존성이 전혀 없는 순수 비즈니스 로직과 모델입니다.
    *   `models/`: 데이터 구조 정의 (Pydantic)
    *   `interfaces/`: 외부 시스템 사용을 위한 추상 클래스(Protocol/ABC) 정의

2.  **Use Cases (Application)**
    *   실제 비즈니스 흐름(시나리오)을 담당합니다.
    *   `Domain` 계층의 모델을 사용하고, `Infrastructure`의 구현체를 주입받아 동작합니다.

3.  **Infrastructure (Adapters)**
    *   `Domain`의 인터페이스를 실제로 구현하는 계층입니다.
    *   외부 라이브러리(BeautifulSoup, Neo4j Driver 등)가 이곳에서만 사용됩니다.

4.  **Interfaces (Presentation/Drivers)**
    *   시스템의 진입점입니다.
    *   API 요청이나 CLI 명령을 받아 `Use Cases`를 호출합니다.
