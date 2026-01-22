# feat(spec-027): implement trafilatura web scraper

## 📋 Summary
<!-- Korean: High-level summary of changes. Use "Before/After" if applicable. -->
기존의 `BasicWebScraper` (`requests` + `markdownify`)는 HTML 전체를 단순 변환하여 광고 및 잡음이 포함되는 문제가 있었습니다.
이를 해결하기 위해 오픈소스 라이브러리인 **`trafilatura`**를 도입하여, 비용 발생 없이 본문(Article)만 정밀하게 추출하고 메타데이터를 확보하도록 개선했습니다.

## 🎯 Key Review Points
<!-- Korean: Specific areas requiring user attention. -->
1. **Trafilatura Adoption**: `TrafilaturaWebScraper` 구현체의 적절성
2. **Fallback Logic**: 추출 실패 시 예외 처리 방식
3. **Dependency Injection**: `dependencies.py`에서 정상적으로 교체되었는지

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests (Mocking HTML validation)
uv run pytest tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py

# Integration Tests (API wiring check)
uv run pytest tests/integration/test_ingestion_api.py
```

### Manual Verification
1. `POST /ingest/web` 엔드포인트 호출
2. 반환된 Markdown에서 광고/메뉴가 제거되었는지 확인

## 📦 Files Changed

### 🆕 New Files
- `app/infrastructure/scrapers/trafilatura_scraper.py`: Trafilatura 기반 스크래퍼 구현체
- `tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py`: 스크래퍼 단위 테스트

### 🛠 Modified Files
- `app/interfaces/api/dependencies.py` (+1, -1): `get_scraper` 의존성 교체
- `pyproject.toml` (+1): `trafilatura` 의존성 추가
- `uv.lock`: 의존성 잠금 파일 갱신

## ✅ Definition of Done
- [x] Dependency Added (`trafilatura`)
- [x] Unit/Integration Tests Pass
- [x] Walkthrough Evidence Created
