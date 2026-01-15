# 🚀 Feature: Spec 002 - Atomic Storage & Swagger Admin

## 📝 Summary
**Spec 002**에서는 수집된 데이터를 영구 저장하기 위한 **DB 인프라(Neo4j, ChromaDB)**를 구축하고, API를 통해 이를 관리할 수 있는 기능을 구현했습니다.
특히 **DDD(Domain-Driven Design)** 패턴을 도입하여 도메인 모델(`Entities`, `Value Objects`)을 명확히 하고, **Composite Storage Pattern**을 통해 이기종 DB 저장을 추상화했습니다.

---

## 🔍 Key Review Points (중점 확인 사항)

### 1. 🏗️ DDD Architecture Adoption (`docs/architecture.md`)
- `app/domain` 하위가 `entities`, `value_objects`, `interfaces`로 명확히 분리되었는지(DDD Tactics).
- `AtomicDocument`가 식별자(ID)를 가진 엔티티로 잘 정의되었는지.

### 2. 💾 Composite Storage (`app/infrastructure/storage/composite.py`)
- `Neo4j`(Graph)와 `Chroma`(Vector)를 하나의 `save()` 호출로 처리하는 Facade 패턴 구현이 적절한지.

### 3. 🔌 Dependency Injection (`app/interfaces/api/main.py`)
- `DocumentRepository` 인터페이스를 통해 구체적인 DB 구현체가 `IngestionService`에 주입되는지.

---

## 🧪 Verification Plan

### 1. Automated Tests 🟢
Mocking을 통해 Repository 의존성을 제거한 상태로 로직 검증.
```bash
PYTHONPATH=. uv run pytest tests/unit/test_storage.py tests/integration/test_api_ingest.py
```

### 2. Manual Test (Database Connection) 🐳
실제 DB 연결 테스트는 Docker 환경이 필요합니다.
```bash
# 1. 인프라 실행
docker compose up -d

# 2. 서버 실행
uv run uvicorn app.interfaces.api.main:app --reload

# 3. 데이터 저장 요청
curl -X POST "http://localhost:8000/ingest/web" -d '{"url": "https://example.com"}'

# 4. 저장 확인
curl "http://localhost:8000/documents"
```

---

## 🛠️ Tech Stack
- **Database**: Neo4j 5.x, ChromaDB
- **Infrastructure**: Docker Compose (via `docker compose`)
- **Design Pattern**: Repository Pattern, Composite Pattern
