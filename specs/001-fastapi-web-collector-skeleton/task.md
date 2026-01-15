# Spec 001: FastAPI & Web Collector Skeleton

## Goal
RAG 인제스션 파이프라인의 핵심 골격인 FastAPI 서버를 구축하고, URL을 입력하면 마크다운으로 변환하는 기본 웹 컬렉터(Web Collector) 기능을 구현합니다. (사용자 정의 Clean Architecture 적용)

## Tasks
- [x] `uv` 기반 프로젝트 초기화 및 의존성 설정
  - [x] `fastapi`, `uvicorn`, `pydantic` 설치
  - [x] `beautifulsoup4`, `markdownify`, `requests` 설치
  - [x] 개발용 `pytest`, `httpx` 설치
- [x] 사용자 정의 Clean Architecture 폴더 구조로 리팩토링
  - [x] `app/core` (설정)
  - [x] `app/domain/models`, `app/domain/interfaces` (엔티티 & 포트)
  - [x] `app/infrastructure/scrapers` (어댑터)
  - [x] `app/use_cases` (유스케이스)
  - [x] `app/interfaces/api` (Web Entry Point)
- [x] 도메인 모델 및 인터페이스 정의
  - [x] `IngestRequest`, `IngestResponse` (app/domain/models)
  - [x] `ScraperInterface` (app/domain/interfaces)
- [x] Infrastructure 계층 구현
  - [x] `BasicWebScraper` (app/infrastructure/scrapers)
- [x] Application 계층 구현
  - [x] `IngestionService` (app/use_cases)
- [x] Interface 계층 구현
  - [x] `POST /ingest/web` 엔드포인트 구축 (app/interfaces/api)
- [x] 문서화 (docs/)
  - [x] `docs/architecture.md`: 폴더 구조 설명
  - [x] `docs/getting_started.md`: 실행 및 테스트 방법
- [x] 테스트 및 검증
  - [x] 단위 테스트 (Scraper, Usecase)
  - [x] 통합 테스트 (API)
