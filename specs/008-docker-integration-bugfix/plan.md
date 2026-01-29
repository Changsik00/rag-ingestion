# Plan: Spec 008 - Docker 통합 환경 버그 픽스 및 안정화

## 📋 목표 요약

Docker 통합 환경에서 발생하는 버그들을 수정하고, 의존성 관리를 개선하여 안정적인 개발 환경을 구축합니다.

## 🔍 발견된 문제 (Identified Issues)

### 1. Neo4jStorage 생성자 불일치 ⚠️ CRITICAL
**현상:**
- `app/infrastructure/storage/neo4j.py` Line 9: `__init__(self)` - 매개변수 없음
- `app/interfaces/api/dependencies.py` Line 39: `Neo4jStorage(driver)` - Driver 전달

**영향:**
- `GET /documents` 호출 시 500 에러 발생
- 런타임에 `TypeError: __init__() takes 1 positional argument but 2 were given` 발생 가능

**근본 원인:**
- Spec 002에서 Neo4jStorage를 처음 구현할 때는 자체적으로 Driver를 생성했음
- 이후 dependency injection 패턴을 도입하면서 dependencies.py만 수정되고, Neo4jStorage 생성자는 업데이트되지 않음

### 2. Docker 의존성 관리 문제 ⚠️ MEDIUM
**현상:**
- `docker-compose.yml` Line 39에서 `pip install` 직접 실행
- `pyproject.toml`에 정의된 의존성을 활용하지 못함

**영향:**
- 의존성 버전 불일치 가능성
- 의존성 누락 가능성 (사용자가 수동으로 추가해야 함)
- 느린 빌드 시간 (매번 pip install 실행)
- Docker 이미지 크기 최적화 불가

### 3. test_scraper.py Import 에러 ⚠️ LOW
**현상:**
- `tests/unit/test_scraper.py` Line 3: `from app.domain.models.ingest import IngestResponse`
- 실제로는 `app.schemas.ingest`에 있음

**영향:**
- pytest 실행 시 collection 에러
- 24개 테스트 중 1개 테스트 파일을 실행할 수 없음

---

## 🛠 제안된 변경사항 (Proposed Changes)

### Component 1: Infrastructure - Storage Layer

#### [MODIFY] [neo4j.py](file:///Users/ck/Project/doit/rag-ingestion/app/infrastructure/storage/neo4j.py)

**변경 내용:**
```python
# Before (Line 9-13)
class Neo4jStorage(DocumentRepository):
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

# After
class Neo4jStorage(DocumentRepository):
    def __init__(self, driver: Driver):
        self.driver = driver
    
    # close() 메서드는 유지 (하위 호환성)
```

**근거:**
- Dependency Injection 원칙 준수
- 테스트 시 Mock Driver 주입 가능 (단위 테스트 개선)
- dependencies.py의 기대값과 일치

---

### Component 2: Docker Configuration

#### [NEW] [Dockerfile](file:///Users/ck/Project/doit/rag-ingestion/Dockerfile)

**내용:**
```dockerfile
FROM python:3.12-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (uv 사용)
RUN uv sync --frozen --no-dev

# 소스 코드 복사
COPY . .

# FastAPI 실행
CMD ["uv", "run", "uvicorn", "app.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**근거:**
- `pyproject.toml` 기반 의존성 관리
- `uv`를 활용한 빠른 설치 속도
- 의존성 레이어 캐싱으로 빌드 시간 최적화

#### [MODIFY] [docker-compose.yml](file:///Users/ck/Project/doit/rag-ingestion/docker-compose.yml)

**변경 내용:**
```yaml
# Before (Line 24-42)
  backend:
    image: python:3.9-slim
    container_name: rag-backend
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    working_dir: /app
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
    command: >
      sh -c "pip install fastapi uvicorn neo4j chromadb requests beautifulsoup4 lxml markdownify pydantic python-dotenv langchain langchain-google-genai && uvicorn app.interfaces.api.main:app --host 0.0.0.0 --port 8000"
    depends_on:
      - neo4j
      - chromadb

# After
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rag-backend
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - CHROMA_HOST=chromadb
      - CHROMA_PORT=8000
    depends_on:
      - neo4j
      - chromadb
```

**근거:**
- Custom Dockerfile 사용으로 의존성 관리 일원화
- `working_dir` 제거 (Dockerfile에서 처리)
- `command` 제거 (Dockerfile CMD 사용)

---

### Component 3: Tests - Unit Tests

#### [MODIFY] [test_scraper.py](file:///Users/ck/Project/doit/rag-ingestion/tests/unit/test_scraper.py)

**변경 내용:**
```python
# Before (Line 3)
from app.domain.models.ingest import IngestResponse

# After
from app.schemas.ingest import IngestRequest
```

**근거:**
- 실제 모듈 경로와 일치
- pytest collection 에러 해결

---

## ✅ 검증 계획 (Verification Plan)

### 1. 자동화된 테스트 (Automated Tests)

#### 1.1 Unit Tests
```bash
# 전체 단위 테스트 실행
uv run pytest tests/unit/ -v

# 예상 결과: 모든 테스트 통과 (이전 24개 + scraper 테스트)
```

**검증 항목:**
- [x] `test_scraper.py` import 에러 해결
- [x] 모든 기존 테스트 통과
- [x] 새로운 테스트 추가 불필요 (구조 변경만 있음)

#### 1.2 Integration Tests
```bash
# 통합 테스트 실행
uv run pytest tests/integration/ -v

# 예상 결과: /documents 엔드포인트 테스트 통과
```

**검증 항목:**
- [x] `test_list_documents_endpoint` 통과
- [x] `test_async_ingest_web_endpoint` 통과
- [x] `test_jobs.py` 모든 테스트 통과

### 2. 수동 검증 (Manual Verification)

#### 2.1 Docker 환경 빌드 및 실행
```bash
# 1. 기존 컨테이너 및 볼륨 정리
docker-compose down -v

# 2. 새로운 이미지 빌드 및 실행
docker-compose up --build

# 예상 결과:
# - backend 컨테이너가 정상적으로 시작됨
# - "Application startup complete" 메시지 확인
# - Neo4j, ChromaDB 연결 성공
```

**검증 항목:**
- [x] backend 서비스 정상 기동
- [x] 의존성 설치 에러 없음
- [x] 환경 변수 정상 로드

#### 2.2 API 엔드포인트 테스트

**a. Health Check**
```bash
curl http://localhost:8000/health

# 예상 응답: {"status": "ok"}
```

**b. Documents List (주요 버그 수정 확인)**
```bash
# 초기 상태 (빈 리스트 또는 기존 데이터)
curl http://localhost:8000/documents

# 예상 응답: 200 OK (500 에러가 아님)
# 응답 본문: [] 또는 [{...}] (AtomicDocument 리스트)
```

**c. Ingest Web (전체 플로우 테스트)**
```bash
curl -X POST http://localhost:8000/ingest/web \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# 예상 응답: 202 Accepted
# 응답 본문: {"job_id": "<uuid>", "status": "PENDING"}

# 잠시 후 문서 재확인
curl http://localhost:8000/documents

# 예상 응답: 200 OK
# 응답 본문: [{
#   "id": "<uuid>",
#   "content": "...",
#   "source_url": "https://example.com",
#   ...
# }]
```

**d. Swagger UI 확인**
- 브라우저에서 `http://localhost:8000/docs` 접속
- `/documents` 엔드포인트의 스키마 확인
- "Try it out" 기능으로 실제 호출 테스트

#### 2.3 로그 확인
```bash
# backend 로그 실시간 확인
docker-compose logs -f backend

# 확인 항목:
# - Neo4j 연결 성공 로그
# - ChromaDB 연결 성공 로그
# - 에러 스택 트레이스 없음
```

---

## 📦 작업 분할 (Task Breakdown)

### Phase 0: 브랜치 생성
0. `fix/008-docker-integration-bugfix` 브랜치 생성 및 전환

### Phase 1: 코드 수정
1. Neo4jStorage 생성자 수정
2. test_scraper.py import 수정
3. 단위 테스트 실행 및 검증

### Phase 2: Docker 환경 개선
4. Dockerfile 작성
5. docker-compose.yml 수정
6. Docker 빌드 및 실행 테스트

### Phase 3: 통합 검증
7. API 엔드포인트 수동 테스트
8. 전체 플로우 검증 (ingest → store → list)
9. 문제 발견 시 추가 수정

---

## 🚨 리스크 및 대응 방안 (Risks & Mitigation)

### Risk 1: ChromaDB 버전 불일치
**문제:** `pyproject.toml`에는 `chromadb-client`를 사용하지만, 기존 코드는 `chromadb` import 사용

**대응:**
- Dockerfile에서 설치 후 import 테스트 진행
- 필요 시 `chromadb` 패키지로 변경 (pyproject.toml 업데이트)

### Risk 2: .env 파일 미포함
**문제:** Docker 빌드 시 `.env` 파일이 포함되지 않을 수 있음

**대응:**
- `docker-compose.yml`의 `environment` 섹션에서 환경 변수 직접 정의 (현재 구조 유지)
- 또는 `env_file: .env` 지시어 추가

### Risk 3: 볼륨 마운트로 인한 uv sync 충돌
**문제:** `volumes: .:/app`로 인해 로컬 `.venv`가 도커 내부 `.venv`와 충돌

**대응:**
- Dockerfile에서 `uv sync --frozen --no-dev` 사용 (컨테이너 내부 환경 격리)
- 필요 시 `.dockerignore`에 `.venv` 추가

---

## ✅ Definition of Done (DoD)

- [x] Neo4jStorage와 ChromaStorage가 Driver/Client를 외부에서 주입받음
- [x] `tests/unit/test_scraper.py` import 에러 해결
- [x] 전체 Unit 테스트 통과 (24개 이상)
- [x] Backend 서비스가 Dockerfile 기반으로 빌드됨
- [x] `docker-compose up --build`로 전체 환경이 정상 실행됨
- [x] 모든 API 엔드포인트가 정상 응답 반환:
  - `GET /health` → 200 OK
  - `POST /ingest/web` → 202 Accepted
  - `GET /documents` → 200 OK (500 에러 해결 확인)
- [x] Docker 로그에 에러 없음
- [x] Swagger UI에서 스키마 정상 표시
