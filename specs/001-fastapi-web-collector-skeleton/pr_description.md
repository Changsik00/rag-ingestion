# 🚀 Feature: Spec 001 - FastAPI & Web Collector Skeleton

## 📝 Summary
**Spec 001**의 목표인 "Web-to-Markdown" 수집 파이프라인의 **Vertical Slice (MVP)** 를 구현했습니다.
추상적인 설계를 걷어내고, **Clean Architecture** 폴더 구조(`app/`)를 기반으로 실제로 동작하는 **FastAPI 서버**와 **기본 웹 수집기(bs4+markdownify)** 를 완성했습니다.

이제 우리는 URL을 던지면 마크다운을 뱉어내는 "살아있는 수집 엔진"을 갖게 되었습니다! 🎉

---

## 🔍 Key Review Points (중점 확인 사항)

### 1. 🏗️ Clean Architecture Structure (`docs/architecture.md`)
- `app/domain` (Core) -> `app/infrastructure` (Adapter) -> `app/interfaces` (API) 로 이어지는 의존성 방향이 올바른지 확인해주세요.
- 특히 `IngestionService`(UseCase)가 구체적인 `BasicWebScraper`가 아니라 `ScraperInterface`에 의존하고 있는지(DIP)가 핵심입니다.

### 2. 🔌 Dependency Injection (`app/interfaces/api/main.py`)
- FastAPI의 `Dependency Injection` 시스템을 사용하여 `BasicWebScraper`를 주입하는 방식이 적절한지 봐주세요.

### 3. 🧪 Testing Strategy (TDD)
- **Unit Test**: `tests/unit/test_scraper.py` (Mock을 사용한 순수 로직 검증)
- **Integration Test**: `tests/integration/test_api_ingest.py` (실제 API 요청/응답 검증)

---

## 🧪 Verification Plan (어떻게 검증하나요?)

### 1. Automated Tests 🟢
터미널에서 전체 테스트를 실행하여 Pass 여부를 확인합니다.
```bash
PYTHONPATH=. uv run pytest -v
```

### 2. Manual Test (Server Run) 🚀
서버를 띄우고 직접 API를 호출해봅니다.
```bash
# 1. 서버 실행
uv run uvicorn app.interfaces.api.main:app --reload

# 2. API 호출 (새 터미널)
curl -X POST "http://localhost:8000/ingest/web" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```
**기대 결과**: JSON 응답의 `markdown` 필드에 "Example Domain" 내용이 포함되어 있어야 합니다.

---

## 🛠️ Tech Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Package Manager**: uv
- **Scraping**: BeautifulSoup4, Markdownify, Requests
- **Testing**: Pytest, Httpx
