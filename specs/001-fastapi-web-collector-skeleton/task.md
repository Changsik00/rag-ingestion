# Spec 001: FastAPI & Web Collector Skeleton

## Goal
RAG 인제스션 파이프라인의 핵심 골격인 FastAPI 서버를 구축하고, URL을 입력하면 마크다운으로 변환하는 기본 웹 컬렉터(Web Collector) 기능을 구현합니다.

## Tasks
- [x] `uv` 기반 프로젝트 초기화 및 의존성 설정
  - [x] `fastapi`, `uvicorn`, `pydantic` 설치
  - [x] `beautifulsoup4`, `markdownify`, `requests` 설치
  - [x] 개발용 `pytest`, `httpx` 설치
- [ ] Clean Architecture 폴더 구조 생성
  - [ ] `src/adapters/input/api/v1` (API 라우트)
  - [ ] `src/core/domain` (도메인 모델)
  - [ ] `src/core/usecases` (비즈니스 로직)
  - [ ] `src/adapters/output` (스크래퍼 구현체)
- [ ] 도메인 모델 및 포트(Port) 정의
  - [ ] `IngestRequest`, `IngestResponse` 모델 정의
  - [ ] `WebScraperPort` 인터페이스 정의
- [ ] `WebCollector` 어댑터 구현
  - [ ] `BasicWebScraper` (requests + markdownify) 구현
- [ ] `POST /ingest/web` 엔드포인트 구현
  - [ ] 입력: URL 문자열
  - [ ] 출력: 원본 마크다운 및 메타데이터
- [ ] 테스트 작성 및 검증
  - [ ] `BasicWebScraper` 단위 테스트 (Mock 활용)
  - [ ] API 엔드포인트 통합 테스트
