# Implementation Plan: Spec-027 (Intelligent Web Scraping)

## 📋 Branch Strategy
- `feature/spec-027-smart-scraper`

## 🛑 User Review Required
<!-- Korean: Critical items requiring explicit user approval before proceeding -->
<!-- Example: A vs B 선택, Breaking Change 여부 등 -->
- [x] **Library Choice**: `trafilatura`는 정적 페이지에 강하지만 SPA(동적 페이지) 수집 능력은 제한적임. (동적 페이지는 추후 Playwright 등으로 확장 필요)
- [x] **Fallback**: 본문 추출 실패 시, 기존 단순 방식(requests)으로 자동 전환되는 것에 동의하는지.

## 🎯 Core Strategy
<!-- Korean: Key architectural decisions and reasoning -->
<!-- Example: A 방식 대신 B 방식을 선택함. 그 이유는 성능상 이점이 있기 때문임. -->
- **Trafilatura Adoption**: 비용이 들지 않는 오픈소스 중 본문 추출 성능이 가장 우수한 `trafilatura`를 채택함.
- **Interface Segregation**: 기존 `ScraperInterface`를 유지하며 구현체만 교체(`Basic` -> `Trafilatura`)하여 비즈니스 로직 영향 최소화.

## 📂 Proposed Changes
<!-- Group by Component -->

### [Infrastructure Layer]

#### [MODIFY] `app/interfaces/api/dependencies.py`
<!-- Korean: Explanation of changes -->
```python
# 기존 BasicWebScraper 대신 TrafilaturaScraper 주입
def get_scraper() -> ScraperInterface:
    return TrafilaturaWebScraper()
```

#### [NEW] `app/infrastructure/scrapers/trafilatura_scraper.py`
<!-- Korean: Explanation of purpose -->
- `trafilatura` 라이브러리를 사용한 `ScraperInterface` 구현체
- `fetch_url` 및 `extract` 함수 활용하여 Clean Markdown 생성
- 메타데이터(Title, Date, Author) 추출 및 매핑

#### [MODIFY] `pyproject.toml`
<!-- Korean: Explanation of changes -->
- `trafilatura` 의존성 추가

## 🧪 Verification Plan

### Automated Tests
```bash
# Unit Tests (Mocking HTML)
uv run pytest tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py

# Integration Check (if applicable)
uv run pytest tests/integration/test_ingestion_api.py
```

### Manual Verification
1. `fastapi` 서버 실행 (`uv run uvicorn ...`)
2. Swagger UI (`/docs`) 접속
3. `POST /ingest/web` 엔드포인트에 네이버 뉴스/기술 블로그 URL 입력
4. 반환된 Markdown에서 광고/댓글/메뉴가 제거되었는지 확인

