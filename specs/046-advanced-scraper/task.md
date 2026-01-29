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
- [x] `uv add playwright` 실행
- [x] Playwright 브라우저 설치: `uv run playwright install chromium`
- [x] Commit: `chore(spec-046): add playwright dependencies`

---

## Task 2: Infrastructure Layer - Playwright Scraper
### 2-1. TDD Warming up
- [x] Test Case 작성: `tests/unit/infrastructure/scrapers/test_playwright_scraper.py`
- [x] Test 실행 (Fail -> Pass): `uv run pytest ...`
- [x] Commit: `test(spec-046): add playwright scraper unit tests`

### 2-2. Implementation
- [x] `app/infrastructure/scrapers/playwright_scraper.py` 구현
- [x] Test 실행 (Pass): `uv run pytest ...`
- [x] Commit: `feat(spec-046): implement Playwright scraper`

---

## Task 3: Ingestion Logic - Tiered Strategy Integration
### 3-1. Refactoring ScraperService
- [x] `app/infrastructure/scrapers/scraper_service.py` (CompositeScraper) 수정
  - [x] Tiered logic (Fallback) 반영
  - [x] **Semantic / Morphological Guard** 구현 (LLM-as-a-Judge 연동)
  - [x] Async 인터페이스 전환 명시
- [x] Commit: `refactor(spec-046): implement tiered scraping strategy with semantic guard`

---

## Task N: PR Creation & Archiving (Mandatory)
- [x] Code Quality Check: `uv run ruff check . --fix && uv run ruff format .`
- [x] Run Full Tests: `uv run pytest`
- [x] **Walkthrough 작성**: `specs/046-advanced-scraper/walkthrough.md`
- [x] **PR Description 작성**: `specs/046-advanced-scraper/pr_description.md`
- [x] **Archive Commit**: 위 파일을 `specs/`에 커밋
- [x] Create PR: `gh pr create`

## Summary
**총 Task**: 4개 세부 작업군  
**현재 진행**: 완료 (PR #50 생성)
