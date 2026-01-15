# [Spec 001] FastAPI & Web Collector Skeleton

## Goal Description
사용자가 정의한 Clean Architecture 구조에 맞춰 FastAPI 서버와 기본 Web Collector를 구현합니다. `app/` 디렉토리 하위에 계층별로 코드를 배치하고, `uv`를 통해 의존성을 관리합니다.

## User Review Required
> [!NOTE]
> 폴더 구조가 `src/`에서 `app/`으로 변경되었습니다.
> `docs/` 디렉토리에 아키텍처 및 실행 가이드가 추가될 예정입니다.

## Proposed Changes

### Project Configuration
#### [MODIFY] [pyproject.toml](file:///Users/ck/Project/doit/rag-ingestion/pyproject.toml)
- 패키지 탐색 경로 수정 (src -> app)

### Domain Layer (Entities & Interfaces)
#### [NEW] [app/domain/models/ingest.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/models/ingest.py)
- `IngestRequest`, `IngestResponse`

#### [NEW] [app/domain/interfaces/scraper.py](file:///Users/ck/Project/doit/rag-ingestion/app/domain/interfaces/scraper.py)
- `ScraperInterface` (Abstract Base Class)

### Infrastructure Layer (Adapters)
#### [NEW] [app/infrastructure/scrapers/basic.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/scrapers/basic.py)
- `BasicWebScraper` (Implementation)

### Use Case Layer (Application)
#### [NEW] [app/use_cases/ingestion.py](file:///Users/ck/Project/doit/rag-ingestion/app/use_cases/ingestion.py)
- `ingest_web_page` (Service function)

### Interface Layer (Drivers)
#### [NEW] [app/interfaces/api/main.py](file:///Users/ck/Project/doit/rag-ingestion/app/interfaces/api/main.py)
- FastAPI App Entry Point
- DI Wiring

## Verification Plan

### Documentation Verification
- `docs/architecture.md` 확인
- `docs/getting_started.md` 확인

### Automated Tests
- **Unit Tests**: `tests/unit/test_scraper.py`
- **Integration Tests**: `tests/integration/test_api_ingest.py`

### Manual Verification
- `uv run uvicorn app.interfaces.api.main:app --reload`
