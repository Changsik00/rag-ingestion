# Task List: Spec-039 (Refined)

## Progress
- [x] Spec 번호 확정 (039)
- [x] spec.md 업데이트 (Expert Advice 반영)
- [x] plan.md 업데이트 (Firecrawl & Cleaner 중심)
- [x] task.md 업데이트
- [x] 백로그 업데이트
- [ ] User Plan Accept

## Task 1: Pollution Control & Cleaning Engine
### 1-1. Markdown Cleaner Implementation
- [ ] `MarkdownCleaner` 구현: 정규식을 이용한 Wiki 노이즈(`[1]`, `[편집]`), 빈 링크, 특수문자 제거.
- [ ] Test: `tests/unit/infrastructure/scraper/test_cleaner.py` (나무위키 샘플 데이터 활용)
- [ ] Commit: `feat(spec-039): implement markdown cleaner for pollution control`

## Task 2: Advanced Scrapers (Firecrawl & Playwright)
### 2-1. Firecrawl Scraper
- [ ] `FirecrawlWebScraper` 구현: 시맨틱 구조 보존 옵션 적용.
- [ ] Commit: `feat(spec-039): implement firecrawl-based semantic scraper`

### 2-2. Playwright Scraper (Skeleton)
- [ ] `PlaywrightWebScraper` 인터페이스 구현 (향후 확장을 위한 뼈대).
- [ ] Commit: `feat(spec-039): add playwright scraper for custom extensions`

## Task 3: Intelligent Fallback & Quality Check
### 3-1. Quality Checker
- [ ] `ScrapingQualityChecker` 구현: 300자 미만, JS Blocked 키워드, 구조 부실 탐지 루틴.
- [ ] Commit: `feat(spec-039): implement heuristic quality checker for fallback triggers`

### 3-2. Composite Controller
- [ ] Trafilatura -> Firecrawl -> (Optional) Playwright 흐름 완성.
- [ ] Commit: `feat(spec-039): complete tiered hybrid scraping workflow`

## Task 4: Verification & Comparison Tooling
### 4-1. Comparison Utility
- [ ] `scripts/compare_scrapers.py` 구현: Side-by-side 파일 저장 및 성능 리포트.
- [ ] Commit: `tool(spec-039): add scraper comparison utility`

## Task 5: Final Verification
- [ ] Code Quality Check & Full test execution.
- [ ] Create PR.

## Summary
**총 Task**: 7개 주요 세부 단계
**예상 커밋 수**: 10~12개
