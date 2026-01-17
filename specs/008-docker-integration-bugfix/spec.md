# Spec 008: Docker 통합 환경 버그 픽스 및 안정화

## 📌 목적 (Purpose)

현재 Docker 환경에서 발생하고 있는 여러 버그를 수정하고, 통합 환경의 안정성을 확보합니다.

### 발견된 문제

1. **Neo4jStorage 생성자 불일치**
   - `app/infrastructure/storage/neo4j.py`의 `__init__` 메서드는 매개변수를 받지 않음
   - `app/interfaces/api/dependencies.py`에서는 `Neo4jStorage(driver)`로 Driver를 전달
   - 결과: 런타임 에러 발생

2. **Docker 의존성 관리 문제**
   - `docker-compose.yml`에서 `pip install`을 직접 실행
   - `pyproject.toml`에 정의된 의존성을 활용하지 못하고 있음
   - 결과: 의존성 불일치, 누락 가능성, 빌드 시간 증가

3. **API 엔드포인트 에러**
   - `GET /documents` 호출 시 500 에러 발생
   - 원인: Neo4jStorage 생성자 문제로 인한 초기화 실패

## 🎯 목표 (Goals)

1. **Neo4jStorage 생성자 수정**: Driver 인스턴스를 외부에서 주입받도록 변경
2. **Docker 환경 개선**: Dockerfile 기반 빌드로 전환하여 `pyproject.toml` 활용
3. **통합 테스트 검증**: Docker Compose 환경에서 모든 API 엔드포인트 정상 동작 확인

## 🔧 기술적 접근 (Technical Approach)

### 1. Neo4jStorage 리팩토링
```python
class Neo4jStorage(DocumentRepository):
    def __init__(self, driver: Driver):  # Driver를 외부에서 주입
        self.driver = driver
```

### 2. Backend Dockerfile 생성
- `uv`를 활용하여 `pyproject.toml`의 의존성 설치
- Multi-stage build로 이미지 크기 최적화

### 3. docker-compose.yml 수정
- backend 서비스를 custom Dockerfile로 변경
- 기존 inline `pip install` 제거

## 📋 범위 (Scope)

### In-Scope
- ✅ Neo4jStorage 생성자 수정
- ✅ ChromaStorage 생성자 검토 (일관성 확인)
- ✅ Backend Dockerfile 작성
- ✅ docker-compose.yml 수정
- ✅ 통합 테스트 (Docker 환경)

### Out-of-Scope
- ❌ 새로운 기능 추가
- ❌ API 스키마 변경
- ❌ 데이터베이스 스키마 변경

## ✅ Definition of Done (DoD)

1. Neo4jStorage와 ChromaStorage가 모두 Driver/Client를 외부에서 주입받음
2. Backend 서비스가 Dockerfile 기반으로 빌드됨
3. `docker-compose up`으로 전체 환경이 정상 실행됨
4. 모든 API 엔드포인트가 정상 응답 반환:
   - `GET /health` → 200 OK
   - `POST /ingest/web` → 202 Accepted
   - `GET /documents` → 200 OK (리스트 반환)
5. 기존 Unit 테스트가 모두 통과함

## 📚 참고 자료 (References)

- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [Docker Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- `specs/002-atomic-storage-swagger-admin/` (Neo4j 최초 도입 시 문서)
