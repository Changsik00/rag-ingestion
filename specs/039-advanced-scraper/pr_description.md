# feat(spec-039): advanced scraper with pollution control

## 📋 Summary
기존 Trafilatura 중심의 스크레이퍼를 고도화하여, JS가 복잡하거나 Anti-Bot이 적용된 사이트(나무위키 등)에서도 고품질 마크다운을 추출할 수 있도록 **Tiered Hybrid Scraper Strategy**를 구축했습니다.

- **Before**: Trafilatura 단일 엔진 사용. Dynamic Content나 CAPTCHA 대응 불가. 나무위키 등에서 노이즈가 많음.
- **After**: Trafilatura(Primary) -> Firecrawl(Advanced) 방식의 Fallback 전략 도입. 나무위키 전용 Pollution Control logic 추가.

## 🎯 Key Review Points
1. **CompositeScraper**: Trafilatura 결과가 부실하거나(Length/JS Block) 에러 발생 시 자동으로 Firecrawl로 전환하는 로직.
2. **MarkdownCleaner**: 나무위키의 [편집], [1], [2] 등 불필요한 토큰과 리다이렉트 노이즈를 청소하는 정규식 기반 클리너.
3. **Error Handling**: Firecrawl v4 SDK의 Pydantic 모델 반환 및 404 상태 코드 확인 로직 구현.

## 🧪 Verification
### Automated Tests
```bash
uv run pytest tests/contracts/test_scraper_contract.py
uv run pytest tests/integration/bdd/test_failure_flows.py::test_url_404_fails_job
uv run pytest tests/integration/bdd/test_intent_routing.py
```

### Manual Verification
나무위키(Python 문서)를 대상으로 `scripts/compare_scrapers.py`를 실행하여 Trafilatura(실패/노이즈) 대비 Firecrawl(성공/정제됨) 결과 확인 완료.

## 📦 Files Changed

### 🆕 New Files
- `app/infrastructure/scrapers/firecrawl_scraper.py`: Firecrawl API 연동 구현.
- `app/infrastructure/scrapers/composite_scraper.py`: Fallback 전략 관리.
- `app/infrastructure/scrapers/cleaner.py`: 마크다운 정제 로직.
- `app/infrastructure/scrapers/checker.py`: 품질 검사기.

### 🛠 Modified Files
- `app/interfaces/api/dependencies.py`: `CompositeScraper` 주입.
- `app/core/config.py`: `FIRECRAWL_API_KEY` 설정 추가.
- `pyproject.toml`: `firecrawl-py` 의존성 추가.

**Total:** 7+ files changed

## ✅ Definition of Done
- [x] Tiered fallback logic verified.
- [x] Pollution control for Namuwiki verified.
- [x] Integration tests for 404 cases fixed and passed.
- [x] PR Template followed.
