# Task: Spec 008 - Docker 통합 환경 버그 픽스 및 안정화

## 📋 Planning Phase

- [x] 현재 코드베이스 분석 (버그 원인 파악)
  - [x] Neo4jStorage 생성자 불일치 확인 (dependencies.py L39 vs neo4j.py L9)
  - [x] /documents 엔드포인트 500 에러 원인 파악 (Neo4jStorage 생성자 문제)
  - [x] Docker 의존성 관리 문제 분석 (inline pip install vs pyproject.toml)
  - [x] test_scraper.py import 에러 발견 (app.domain.models → app.schemas)
- [x] Spec 문서 작성 (`spec.md`)
- [x] Plan 문서 작성 (`plan.md`)
- [x] Task 체크리스트 작성 (`task.md`)
- [x] 사용자 리뷰 및 Plan Accept 대기

---

## 🚀 Execution Phase (Plan Accept 후 진행)

### Task 0: Feature 브랜치 생성
- [x] main 브랜치에서 `fix/008-docker-integration-bugfix` 브랜치 생성
- [x] 브랜치 전환 확인 (`git branch --show-current`)

### Task 1: Neo4jStorage 생성자 버그 수정
- [x] `app/infrastructure/storage/neo4j.py` 수정
  - [x] `__init__(self, driver: Driver)` 로 변경
  - [x] 환경변수 기반 연결 로직 제거
  - [x] `from neo4j import Driver` import 추가
- [x] 테스트 실행: `uv run pytest tests/unit/test_storage.py -v`
- [x] 커밋: `fix(infrastructure): correct Neo4jStorage constructor to accept driver`

### Task 2: test_scraper.py import 에러 수정
- [x] `tests/unit/test_scraper.py` Line 3 수정
  - [x] `from app.domain.models.ingest import IngestResponse` 삭제
  - [x] `from app.schemas.ingest import IngestResponse` 추가
- [x] 테스트 실행: `uv run pytest tests/unit/test_scraper.py -v`
- [x] 커밋: `fix(tests): correct import path in test_scraper.py`

### Task 3: 전체 Unit 테스트 검증
- [x] 전체 단위 테스트 실행: `uv run pytest tests/unit/ -v`
- [x] 모든 테스트 통과 확인 (24개 이상)
- [x] 필요 시 추가 수정 후 커밋

### Task 4: Backend Dockerfile 생성
- [x] 프로젝트 루트에 `Dockerfile` 생성
  - [x] Python 3.12-slim 베이스 이미지
  - [x] uv 설치
  - [x] pyproject.toml, uv.lock 복사
  - [x] `uv sync --frozen --no-dev` 실행
  - [x] 소스 코드 복사
  - [x] CMD 설정 (uvicorn 실행)
- [x] 로컬 빌드 테스트: `docker build -t rag-backend .`
- [x] 커밋: `chore(docker): add Dockerfile for backend service`

### Task 5: docker-compose.yml 수정
- [x] `docker-compose.yml` 수정
  - [x] backend 서비스의 `image: python:3.9-slim` 제거
  - [x] `build: { context: ., dockerfile: Dockerfile }` 추가
  - [x] `command` 섹션 제거 (Dockerfile CMD 사용)
  - [x] `working_dir` 제거 (Dockerfile에서 설정)
- [x] 커밋: `chore(docker): use custom Dockerfile for backend service`

### Task 6: Docker 환경 통합 테스트
- [x] 기존 컨테이너 정리: `docker-compose down -v`
- [x] 전체 환경 빌드 및 실행: `docker-compose up --build`
- [x] Backend 컨테이너 정상 기동 확인
- [x] 로그에 에러 없는지 확인: `docker-compose logs backend`

### Task 7: API 엔드포인트 수동 검증
- [x] Health Check: `curl http://localhost:8000/health`
- [x] Documents List (주요 버그): `curl http://localhost:8000/documents`
  - [x] 500 에러가 아닌 200 응답 확인
  - [x] 빈 배열 `[]` 또는 문서 리스트 반환 확인
- [x] Swagger UI 확인: `http://localhost:8000/docs`
- [x] Ingest 전체 플로우 테스트:
  ```bash
  curl -X POST http://localhost:8000/ingest/web \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com"}'
  ```
- [x] 다시 Documents List 확인 (문서 저장 확인)

### Task 8: Integration 테스트 실행
- [x] 통합 테스트 실행: `uv run pytest tests/integration/ -v`
- [x] 모든 테스트 통과 확인
- [x] 실패 시 원인 파악 및 수정

### Task 9: 최종 검증 및 정리
- [x] Ruff Linter 실행: `uv run ruff check .`
- [x] 필요 시 수정: `uv run ruff check . --fix`
- [x] 전체 테스트 재실행: `uv run pytest -v`
- [x] Docker 환경 재확인: `docker-compose up`
- [x] 문제 없으면 커밋: `chore: apply linter fixes`

### Task 10: PR 준비 및 생성
- [x] `specs/008-docker-integration-bugfix/pr_description.md` 작성
  - [x] Summary (변경 개요)
  - [x] Key Changes (주요 변경사항)
  - [x] Bug Fixes (수정된 버그)
  - [x] Verification Results (검증 결과)
- [x] GitHub PR 생성: `gh pr create -F specs/008-docker-integration-bugfix/pr_description.md`
- [x] PR URL 사용자에게 보고
