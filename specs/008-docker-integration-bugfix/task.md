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
- [ ] 사용자 리뷰 및 Plan Accept 대기

---

## 🚀 Execution Phase (Plan Accept 후 진행)

### Task 0: Feature 브랜치 생성
- [ ] main 브랜치에서 `fix/008-docker-integration-bugfix` 브랜치 생성
- [ ] 브랜치 전환 확인 (`git branch --show-current`)

### Task 1: Neo4jStorage 생성자 버그 수정
- [ ] `app/infrastructure/storage/neo4j.py` 수정
  - [ ] `__init__(self, driver: Driver)` 로 변경
  - [ ] 환경변수 기반 연결 로직 제거
  - [ ] `from neo4j import Driver` import 추가
- [ ] 테스트 실행: `uv run pytest tests/unit/test_storage.py -v`
- [ ] 커밋: `fix(infrastructure): correct Neo4jStorage constructor to accept driver`

### Task 2: test_scraper.py import 에러 수정
- [ ] `tests/unit/test_scraper.py` Line 3 수정
  - [ ] `from app.domain.models.ingest import IngestResponse` 삭제
  - [ ] `from app.schemas.ingest import IngestResponse` 추가
- [ ] 테스트 실행: `uv run pytest tests/unit/test_scraper.py -v`
- [ ] 커밋: `fix(tests): correct import path in test_scraper.py`

### Task 3: 전체 Unit 테스트 검증
- [ ] 전체 단위 테스트 실행: `uv run pytest tests/unit/ -v`
- [ ] 모든 테스트 통과 확인 (24개 이상)
- [ ] 필요 시 추가 수정 후 커밋

### Task 4: Backend Dockerfile 생성
- [ ] 프로젝트 루트에 `Dockerfile` 생성
  - [ ] Python 3.12-slim 베이스 이미지
  - [ ] uv 설치
  - [ ] pyproject.toml, uv.lock 복사
  - [ ] `uv sync --frozen --no-dev` 실행
  - [ ] 소스 코드 복사
  - [ ] CMD 설정 (uvicorn 실행)
- [ ] 로컬 빌드 테스트: `docker build -t rag-backend .`
- [ ] 커밋: `chore(docker): add Dockerfile for backend service`

### Task 5: docker-compose.yml 수정
- [ ] `docker-compose.yml` 수정
  - [ ] backend 서비스의 `image: python:3.9-slim` 제거
  - [ ] `build: { context: ., dockerfile: Dockerfile }` 추가
  - [ ] `command` 섹션 제거 (Dockerfile CMD 사용)
  - [ ] `working_dir` 제거 (Dockerfile에서 설정)
- [ ] 커밋: `chore(docker): use custom Dockerfile for backend service`

### Task 6: Docker 환경 통합 테스트
- [ ] 기존 컨테이너 정리: `docker-compose down -v`
- [ ] 전체 환경 빌드 및 실행: `docker-compose up --build`
- [ ] Backend 컨테이너 정상 기동 확인
- [ ] 로그에 에러 없는지 확인: `docker-compose logs backend`

### Task 7: API 엔드포인트 수동 검증
- [ ] Health Check: `curl http://localhost:8000/health`
- [ ] Documents List (주요 버그): `curl http://localhost:8000/documents`
  - [ ] 500 에러가 아닌 200 응답 확인
  - [ ] 빈 배열 `[]` 또는 문서 리스트 반환 확인
- [ ] Swagger UI 확인: `http://localhost:8000/docs`
- [ ] Ingest 전체 플로우 테스트:
  ```bash
  curl -X POST http://localhost:8000/ingest/web \
    -H "Content-Type: application/json" \
    -d '{"url": "https://example.com"}'
  ```
- [ ] 다시 Documents List 확인 (문서 저장 확인)

### Task 8: Integration 테스트 실행
- [ ] 통합 테스트 실행: `uv run pytest tests/integration/ -v`
- [ ] 모든 테스트 통과 확인
- [ ] 실패 시 원인 파악 및 수정

### Task 9: 최종 검증 및 정리
- [ ] Ruff Linter 실행: `uv run ruff check .`
- [ ] 필요 시 수정: `uv run ruff check . --fix`
- [ ] 전체 테스트 재실행: `uv run pytest -v`
- [ ] Docker 환경 재확인: `docker-compose up`
- [ ] 문제 없으면 커밋: `chore: apply linter fixes`

### Task 10: PR 준비 및 생성
- [ ] `specs/008-docker-integration-bugfix/pr_description.md` 작성
  - [ ] Summary (변경 개요)
  - [ ] Key Changes (주요 변경사항)
  - [ ] Bug Fixes (수정된 버그)
  - [ ] Verification Results (검증 결과)
- [ ] GitHub PR 생성: `gh pr create -F specs/008-docker-integration-bugfix/pr_description.md`
- [ ] PR URL 사용자에게 보고
