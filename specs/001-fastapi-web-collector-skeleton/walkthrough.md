# Spec 001 Walkthrough: FastAPI & Web Collector Skeleton

## 1. Overview
사용자 정의 **Clean Architecture**를 기반으로 FastAPI 서버와 웹 수집(Web Collector)의 Vertical Slice를 구현했습니다.

## 2. Architecture Implemented
`docs/architecture.md`에 정의된 구조를 준수했습니다.
- **app/domain**: `IngestRequest`, `ScraperInterface` (No dependencies)
- **app/infrastructure**: `BasicWebScraper` (Depend on Interface & 3rd party)
- **app/use_cases**: `IngestionService` (Depend on Interface)
- **app/interfaces**: `FastAPI` (Depend on UseCase)

## 3. Verification Result

### ✅ Automated Tests
모든 계층의 테스트가 통과했습니다.
- **Infrastructure (Unit)**: `BasicWebScraper`가 Mock HTML을 정상 파싱.
- **Application (Unit)**: `IngestionService`가 Scraper를 올바르게 호출.
- **Interface (Integration)**: `POST /ingest/web` 엔드포인트가 200 OK 응답.

```bash
tests/unit/test_scraper.py ..                                          [ 66%]
tests/unit/test_usecases.py .                                          [100%]
tests/integration/test_api_ingest.py .                                 [100%]
```

### ✅ Manual Verification (Example)
`docs/getting_started.md`의 가이드에 따라 서버를 구동하고 테스트했습니다.

```json
// POST http://localhost:8000/ingest/web
{
    "url": "http://example.com/",
    "markdown": "# Example Domain\n\nThis domain is for use in illustrative examples...",
    "metadata": {
        "status_code": 200,
        "content_type": "text/html; charset=UTF-8"
    }
}
```

## 4. Next Steps
- `backlog/queue.md` 업데이트 (Spec 001 완료 처리)
- 다음 스펙 (Neo4j/ChromaDB 연동) 진행
