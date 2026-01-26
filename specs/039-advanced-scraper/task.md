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
- [x] `MarkdownCleaner` 구현: 정규식을 이용한 Wiki 노이즈(`[1]`, `[편집]`), 빈 링크, 특수문자 제거.
- [x] Test: `tests/unit/infrastructure/scrapers/test_markdown_cleaner.py` (나무위키 샘플 데이터 활용)
- [x] Commit: `feat(spec-039): implement markdown cleaner for pollution control`

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
- [ ] `scripts/compare_scrapers.py` 구현: CLI로 URL을 입력받아 각 엔진별 개별 결과 파일(.md) 저장 및 요약 통계 출력.
- [ ] Commit: `tool(spec-039): add scraper comparison utility`

## Task 5: Verification & PR Creation (Protocol Compliance)
### 5-1. Pre-PR Quality Check
- [ ] Code Quality: `uv run ruff check . --fix && uv run ruff format .`
- [ ] Full Tests: `uv run pytest` (모든 테스트 통과 확인)
- [ ] Commit: `chore(spec-039): final code quality and test verification`

### 5-2. Documentation & Artifacts
- [ ] Walkthrough 작성: `specs/039-advanced-scraper/walkthrough.md` (스크린샷/로그 포함)
- [ ] PR Description 작성: `docs/protocols/templates/pr_description.md`를 복사하여 `specs/039-advanced-scraper/pr_description.md` 작성 (한글 사용)
- [ ] Commit: `docs(spec-039): add walkthrough and pr description artifacts`

### 5-3. Create Pull Request
- [ ] PR 생성: `gh pr create --title "feat(spec-039): advanced scraper with pollution control" --body-file specs/039-advanced-scraper/pr_description.md`

## Summary
**총 Task**: 7개 주요 세부 단계
**예상 커밋 수**: 10~12개
