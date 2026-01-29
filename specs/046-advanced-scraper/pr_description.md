# feat(spec-046): implement advanced tiered scraper with semantic quality guard

## 📋 Summary
기존의 단일 정적 스크래핑 방식에서 **3단계 계층적 전략(Tiered Strategy)**으로 고도화하여 수집 성공률과 데이터 품질을 획득했습니다. 특히 Playwright를 도입하여 유료 API 비용 없이도 나무위키 등 동적 사이트를 지원하며, LLM 기반의 시맨틱 분석으로 부실 데이터를 자동으로 걸러냅니다.

## 🎯 Key Review Points
1. **Tiered Fallback Logic**: `CompositeScraper`에서 Trafilatura(Tier 1) -> Playwright(Tier 2) -> Firecrawl(Tier 3)로 이어지는 전환 로직
2. **Semantic Quality Guard**: `ScrapingQualityChecker`에 구현된 형태소 분석 휴리스틱 및 LLM 시맨틱 판독 로직
3. **Async Infrastructure**: Playwright 지원을 위해 전체 스크래퍼 인터페이스 및 인제스션 서비스를 비동기화(`async/await`)

## 🧪 Verification
### Automated Tests
```bash
uv run pytest tests/unit/infrastructure/scrapers/test_playwright_scraper.py
```
- 모든 테스트(3종) 통과 완료.

### Manual Verification
- 나무위키 및 동적 JS 렌더링 사이트에 대해 Playwright 정상 동작 확인.
- 명사 위주의 메뉴 파편 수집 시 품질 가드가 작동하여 다음 티어로 전환됨을 확인.

## 📂 Files Changed
- [NEW] `app/infrastructure/scrapers/playwright_scraper.py`
- [MODIFY] `app/infrastructure/scrapers/composite_scraper.py`
- [MODIFY] `app/infrastructure/scrapers/checker.py`
- [MODIFY] `app/use_cases/ingestion.py`
- [MODIFY] `app/domain/interfaces/scraper.py`
- [MODIFY] `app/infrastructure/scrapers/trafilatura_scraper.py`
- [MODIFY] `app/infrastructure/scrapers/firecrawl_scraper.py`
- [NEW] `tests/unit/infrastructure/scrapers/test_playwright_scraper.py`

## ✅ Definition of Done
- [x] Playwright 기반 동적 수집 로직 구현
- [x] 계층적 3단계 전환 로직 구현 (무료 도구 우선)
- [x] 시맨틱/형태소 기반 품질 가드 구현
- [x] 전체 파이프라인 비동기화 완료
- [x] 유닛 테스트 통과
