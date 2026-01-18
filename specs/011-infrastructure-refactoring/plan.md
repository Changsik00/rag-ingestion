# Implementation Plan: Spec 011 - Infrastructure Refactoring

## 📋 Summary

Infrastructure Layer의 파일명 표준화, 주석 한글 통일, Clean Architecture 개선을 통해 코드 품질과 유지보수성을 향상합니다.

**주요 변경점:**
1. Repository 구현 파일명을 Interface 이름과 일치하도록 변경
2. 모든 주석을 한글로 통일 (도메인 용어는 영어 유지)
3. Type hints 및 주석 개선

**⚠️ 중요:** 기능 변경 없음, 리팩토링만 수행

---

## 🎯 User Review Required

> [!IMPORTANT]
> 파일명 변경으로 인한 Git history 영향
> 
> 파일명 변경 시 Git이 파일 이동으로 인식하지만, `git log --follow` 없이는 히스토리 추적이 어려울 수 있습니다.
> 
> **대안:**
> - 현재 방식: `git mv` 사용 (권장)
> - 더 안전한 방식: 새 파일 생성 후 deprecation 경고 (과함)

---

## 📝 Proposed Changes

### Phase 1: 파일명 변경

#### Infrastructure Storage Layer

**1. `neo4j.py` → `neo4j_document_repository.py`**
```bash
git mv app/infrastructure/storage/neo4j.py app/infrastructure/storage/neo4j_document_repository.py
```

**변경 이유:**
- DocumentRepository 구현체임을 명확히
- Interface 이름(`document_repository.py`)과 일치

**2. `neo4j_graph.py` → `neo4j_graph_repository.py`**
```bash
git mv app/infrastructure/storage/neo4j_graph.py app/infrastructure/storage/neo4j_graph_repository.py
```

**변경 이유:**
- `_graph` vs `_graph_repository` 일관성
- `neo4j_graph.py`는 역할이 불분명

**3. `neo4j_job_repo.py` → `neo4j_job_repository.py`**
```bash
git mv app/infrastructure/storage/neo4j_job_repo.py app/infrastructure/storage/neo4j_job_repository.py
```

**변경 이유:**
- `_repo` 줄임말 대신 full name
- 다른 Repository 파일명과 일관성

---

### Phase 2: Import 경로 업데이트

#### 영향받는 파일 (예상 10개)

**1. `app/interfaces/api/dependencies.py`**
```python
# Before
from app.infrastructure.storage.neo4j import Neo4jStorage
from app.infrastructure.storage.neo4j_graph import Neo4jGraphRepository
from app.infrastructure.storage.neo4j_job_repo import Neo4jJobRepository

# After
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
```

**2. `app/infrastructure/storage/composite.py`**
```python
# Before
from app.infrastructure.storage.neo4j import Neo4jStorage

# After
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
```

**3. Tests**
- `tests/unit/test_storage.py` (if exists)
- `tests/contracts/test_storage_contract.py`
- 기타 storage import하는 테스트

---

### Phase 3: 주석 한글화

#### 변경 원칙
```python
# ❌ Bad (영어)
# Save to Graph (Structure & Metadata)

# ✅ Good (한글, 도메인 용어는 영어 유지)
# Graph DB에 저장 (구조 및 메타데이터)

# ❌ Bad (설명 부족)
# Flatten metadata

# ✅ Good (상세 설명)
# Neo4j는 primitive 타입만 속성으로 허용하므로 복잡한 타입은 JSON 직렬화
```

#### 주요 변경 파일

**1. `neo4j_document_repository.py` (구 neo4j.py)**
```python
# Before
# Flatten metadata to avoid nested map errors in Neo4j
# Neo4j only allows primitives and arrays of primitives as property values

# After  
# Neo4j는 중첩된 map을 지원하지 않으므로 metadata를 평탄화
# 속성 값으로 primitive 타입(str, int, float, bool)과 배열만 허용됨
```

**2. `chroma.py`**
```python
# Before
# Flatten metadata to comply with ChromaDB constraints
# ChromaDB only accepts str, int, float, bool as metadata values

# After
# ChromaDB 제약사항: metadata 값으로 str, int, float, bool만 허용
# 복잡한 타입은 JSON 문자열로 직렬화하여 저장
```

**3. `dependencies.py`**
```python
# Before
# Scraper dependency
# Neo4j driver dependency  

# After
# === Dependency Injection 컨테이너 ===
# FastAPI의 Depends를 사용하여 각 레이어의 구현체를 주입

# Scraper 의존성
# 웹 페이지 스크래핑 구현체 제공

# Neo4j Driver 의존성
# 모든 Neo4j 저장소가 공유하는 단일 Driver 인스턴스
```

**4. `composite.py`**
```python
# Before
# Save to Graph (Structure & Metadata)
# Save to Vector (Embedding)

# After
# CompositeStorage: 여러 저장소를 조합하여 사용하는 Facade 패턴
# - Neo4j: 구조화된 데이터 및 메타데이터 저장
# - ChromaDB: 벡터 임베딩 저장 (의미 기반 검색용)

def save(self, document: AtomicDocument) -> None:
    # Graph DB에 저장 (구조 및 메타데이터)
    self.graph_storage.save(document)
    # Vector DB에 저장 (임베딩)
    self.vector_storage.save(document)
```

---

### Phase 4: Clean Architecture 개선

#### Type Hints 완성

**`chroma.py`**
```python
# Before
def list_documents(self, limit: int = 10):
    # ...

# After
def list_documents(self, limit: int = 10) -> list[AtomicDocument]:
    # ...
```

#### Docstring 추가 (선택)

**`composite.py`**
```python
class CompositeStorage:
    """
    여러 저장소를 조합하여 사용하는 Composite 패턴 구현
    
    Document를 Graph DB(Neo4j)와 Vector DB(ChromaDB)에 동시 저장하여
    구조화된 쿼리와 의미 기반 검색을 모두 지원합니다.
    
    Attributes:
        graph_storage: 구조화된 데이터 저장 (Neo4j)
        vector_storage: 벡터 임베딩 저장 (ChromaDB)
    """
```

---

## 🧪 Verification Plan

### Automated Tests

**1. Contract Tests**
```bash
uv run pytest tests/contracts/ -v
```
**예상 결과:** 45 passed, 2 skipped (기존과 동일)

**2. Unit Tests**
```bash
uv run pytest tests/unit/ -v
```
**예상 결과:** 모든 테스트 통과

**3. Integration Tests** 
```bash
docker compose up -d
uv run pytest tests/integration/ -v -m integration
```
**예상 결과:** 모든 테스트 통과

### Linter 검증

**Ruff**
```bash
ruff check app/
```
**예상 결과:** 경고 없음

### Manual Verification

**1. Import 검증**
```bash
python -c "
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.infrastructure.storage.neo4j_job_repository import Neo4jJobRepository
print('All imports successful!')
"
```

**2. API 동작 확인**
```bash
# Docker 실행
docker compose up -d

# Health check
curl http://localhost:8000/health

# Document 수집 (Entity 구축 포함)
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html", "enable_extraction": true}'

# 결과 확인
curl http://localhost:8000/documents?limit=5
curl http://localhost:8000/entities?limit=5
```

---

## 📊 File Changes Summary

**파일명 변경 (3개):**
- `neo4j.py` → `neo4j_document_repository.py`
- `neo4j_graph.py` → `neo4j_graph_repository.py`
- `neo4j_job_repo.py` → `neo4j_job_repository.py`

**수정 (예상 15개):**
- `dependencies.py` - import 경로
- `composite.py` - import 경로, 주석
- `chroma.py` - 주석, type hints
- `basic.py` - 주석
- `cypher_queries.py` - 주석
- `*.py` (app 전체) - 주석 한글화
- Tests - import 경로

**신규:** 없음  
**삭제:** 없음

---

## ⏱️ 예상 소요 시간

- Phase 1 (파일명 변경): 10분
- Phase 2 (Import 업데이트): 20분
- Phase 3 (주석 한글화): 60분
- Phase 4 (Clean Architecture): 30분
- 테스트 및 검증: 30분

**Total:** ~2.5시간

---

**작성일:** 2026-01-18  
**관련 Spec:** Spec 006 (Clean Architecture Refactoring)
