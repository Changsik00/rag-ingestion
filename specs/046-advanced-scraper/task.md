# Task List: Spec 046 - Advanced Scraper

## Progress
- [x] Spec 번호 확정 및 브랜치 생성 (`feature/046-advanced-scraper`)
- [x] spec.md 작성 (High-Quality 스타일)
- [x] plan.md 작성 (High-Quality 스타일)
- [x] task.md 작성 (현 파일)
- [x] 백로그 업데이트 (Note 추가)
- [x] User Plan Accept

---

## Task 1: Environment Setup
### 1-1. Dependencies
- [/] `uv add playwright` 실행
- [/] Playwright 브라우저 설치: `uv run playwright install chromium`
- [ ] Commit: `chore(spec-046): add playwright dependencies`

---

## Task 2: Infrastructure Layer - Playwright Scraper
### 2-1. TDD Warming up
- [ ] Test Case 작성: `tests/unit/infrastructure/scrapers/test_playwright_scraper.py`
- [ ] Test 실행 (Fail): `uv run pytest ...`
- [ ] Commit: `test(spec-046): add playwright scraper unit tests`

### 2-2. Implementation
- [ ] `app/infrastructure/scrapers/playwright_scraper.py` 구현
  - `ScraperInterface` 준수
  - Async context manager를 활용한 브라우저 관리
  - Markdown 정제 로직 포함
- [ ] Test 실행 (Pass): `uv run pytest ...`
- [ ] Commit: `feat(spec-046): implement Playwright scraper`

---

## Task 3: Ingestion Logic - Tiered Strategy Integration
### 3-1. Refactoring ScraperService
- [ ] `app/infrastructure/scrapers/scraper_service.py` 수정
  - Tiered logic (Fallback) 반영
  - **Semantic / Morphological Guard** 구현 (LLM-as-a-Judge 연동)
  - Content length-based fallback 트리거 추가
  - (Optional) Firecrawl 연동을 위한 인터페이스(Placeholder) 준비
- [ ] Commit: `refactor(spec-046): implement tiered scraping strategy`

---

## Task N: PR Creation & Archiving (Mandatory)
- [ ] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Run Full Tests: `uv run pytest`
- [ ] **Walkthrough 작성**: `specs/046-advanced-scraper/walkthrough.md`
- [ ] **PR Description 작성**: `specs/046-advanced-scraper/pr_description.md`
- [ ] **Archive Commit**: 위 파일을 `specs/`에 커밋
- [ ] Create PR: `gh pr create --title "feat(spec-046): advanced scraper with playwright" --body-file specs/046-advanced-scraper/pr_description.md`

## Summary
**총 Task**: 4개 세부 작업군  
**예상 커밋 수**: 6개 내외  
**현재 진행**: Planning (Spec/Plan/Task 작성 완료)
