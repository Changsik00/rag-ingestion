# Task List: Spec-027 (Intelligent Web Scraping)

## Progress
- [x] Spec 번호 확정
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [x] User Plan Accept

## Task 1: Environment & Test Setup
### 1-1. Dependency Management
- [x] `pyproject.toml`: trafilatura 추가
- [x] `uv sync` 실행 및 lock 파일 갱신
- [x] Commit: `chore(spec-027): add trafilatura dependency`

### 1-2. TDD Warming up
- [x] Test Case 작성: `tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py`
    - [x] Clean Extraction (Ad removal)
    - [x] Metadata Extraction
    - [x] Fallback Mechanism
- [x] Test 실행 (Fail): `uv run pytest tests/unit/infrastructure/scrapers/test_trafilatura_scraper.py`
- [x] Commit: `test(spec-027): add integration tests for smart scraper`

## Task 2: Implementation
### 2-1. Trafilatura Scraper
- [x] 코드 구현: `app/infrastructure/scrapers/trafilatura_scraper.py`
    - [x] `ScraperInterface` 상속 및 `scrape` 메서드 구현
    - [x] Fallback 로직 추가 (AttributeError/TypeError 방어)
- [x] Test 실행 (Pass)
- [x] Commit: `feat(spec-027): implement trafilatura web scraper`

### 2-2. Service Wiring
- [x] DI 수정: `app/interfaces/api/dependencies.py`
    - [x] `get_scraper`가 `TrafilaturaWebScraper` 반환
- [x] Integration Test 실행 (기존 테스트 호환성 확인)
- [x] Commit: `refactor(spec-027): wire trafilatura scraper to ingestion api`

## Task 3: PR Creation & Delivery
- [x] Code Quality Check: `uv run ruff check . --fix`
- [x] Evidence: `walkthrough.md`에 비포/애프터 비교 추가
- [x] Create PR: `gh pr create`
- [x] Summary in Task.md

## Summary
**총 Task**: 3개
**예상 커밋 수**: 5~6개
