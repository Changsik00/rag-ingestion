# Implementation Plan: Spec 010 - Knowledge Graph Construction

## 📋 Summary

Entity를 Neo4j Graph로 구축하여 지식 베이스 핵심 기능 완성.

**주요 변경점:**
1. `GraphRepository` 인터페이스 정의 (Domain Layer)
2. Cypher Query Templates 도입 (쿼리 중복 제거)
3. `Neo4jGraphRepository` 구현 (Infrastructure Layer) 
4. `IngestionService`에 Entity 그래프 구축 로직 추가
5. Entity 조회 API 엔드포인트 추가

**⚠️ 중요:**
- **LLM 추가 호출 없음** (Spec 005에서 이미 추출된 Entity 사용)
- Entity 간 관계(WORKS_FOR 등)는 향후 별도 Spec에서 구현

---

## 🌳 Branch Strategy

```bash
# 브랜치 생성
git checkout -b feature/010-knowledge-graph-construction

# PR 제목 (squash merge)
feat(spec-010): knowledge graph construction
```

---

## 🔧 Implementation Tasks

### Task 1: Domain Layer - GraphRepository 인터페이스 정의

**파일:** `app/domain/interfaces/graph_repository.py` (신규)

```python
from typing import Protocol
from app.domain.schemas.ontology import EntityType, TypedEntity

class GraphRepository(Protocol):
    """Knowledge Graph 저장소 인터페이스"""
    
    def save_entity(self, name: str, entity_type: EntityType) -> str:
        """Entity 노드 생성/조회 (MERGE)"""
        ...
    
    def create_mention_relationship(
        self, 
        doc_id: str, 
        entity_name: str
    ) -> None:
        """Document-Entity MENTIONS 관계 생성"""
        ...
    
    def get_entities_by_document(self, doc_id: str) -> list[TypedEntity]:
        """특정 Document의 Entity 목록"""
        ...
    
    def get_document_ids_by_entity(self, entity_name: str) -> list[str]:
        """특정 Entity가 언급된 Document ID 목록"""
        ...
    
    def list_all_entities(self, limit: int = 100) -> list[TypedEntity]:
        """전체 Entity 목록"""
        ...
```

---

### Task 2: Infrastructure Layer - Cypher Query Templates

**파일:** `app/infrastructure/storage/cypher_queries.py` (신규)

Cypher 쿼리 중복을 제거하기 위한 Template Strings 정의.

```python
"""Cypher query templates for Knowledge Graph operations"""

# Entity 관련 쿼리
MERGE_ENTITY = """
MERGE (e:Entity {name: $name})
ON CREATE SET 
    e.type = $type,
    e.normalized_name = toLower($name),
    e.created_at = datetime()
RETURN e.name as name
"""

CREATE_ENTITY_INDEX = """
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS 
FOR (e:Entity) REQUIRE e.name IS UNIQUE
"""

# 관계 관련 쿼리
CREATE_MENTIONS_RELATIONSHIP = """
MATCH (d:Document {id: $doc_id})
MATCH (e:Entity {name: $entity_name})
MERGE (d)-[r:MENTIONS]->(e)
ON CREATE SET r.created_at = datetime()
"""

# 조회 쿼리
GET_ENTITIES_BY_DOCUMENT = """
MATCH (d:Document {id: $doc_id})-[:MENTIONS]->(e:Entity)
RETURN e.name as name, e.type as type
"""

GET_DOCUMENT_IDS_BY_ENTITY = """
MATCH (d:Document)-[:MENTIONS]->(e:Entity {name: $entity_name})
RETURN d.id as doc_id
"""

LIST_ALL_ENTITIES = """
MATCH (e:Entity)
RETURN e.name as name, e.type as type
ORDER BY e.type, e.name
LIMIT $limit
"""
```

---

### Task 3: Infrastructure Layer - Neo4jGraphRepository 구현

**파일:** `app/infrastructure/storage/neo4j_graph.py` (신규)

```python
from neo4j import Driver
from app.domain.interfaces.graph_repository import GraphRepository
from app.domain.schemas.ontology import EntityType, TypedEntity
from app.infrastructure.storage import cypher_queries as cq

class Neo4jGraphRepository:
    """Neo4j 기반 Knowledge Graph 저장소"""
    
    def __init__(self, driver: Driver):
        self.driver = driver
        self._create_indexes()
    
    def _create_indexes(self):
        """Entity 검색 성능을 위한 인덱스 생성"""
        with self.driver.session() as session:
            session.run(cq.CREATE_ENTITY_INDEX)
    
    def save_entity(self, name: str, entity_type: EntityType) -> str:
        """Entity 노드 MERGE (중복 시 기존 반환)"""
        with self.driver.session() as session:
            result = session.run(
                cq.MERGE_ENTITY,
                name=name,
                type=entity_type.value
            ).single()
            return result["name"]
    
    def create_mention_relationship(
        self,
        doc_id: str,
        entity_name: str
    ) -> None:
        """Document-Entity MENTIONS 관계 생성"""
        with self.driver.session() as session:
            session.run(
                cq.CREATE_MENTIONS_RELATIONSHIP,
                doc_id=doc_id,
                entity_name=entity_name
            )
    
    def get_entities_by_document(self, doc_id: str) -> list[TypedEntity]:
        """특정 Document의 Entity 목록"""
        entities = []
        with self.driver.session() as session:
            results = session.run(cq.GET_ENTITIES_BY_DOCUMENT, doc_id=doc_id)
            for record in results:
                entities.append(TypedEntity(
                    name=record["name"],
                    type=EntityType(record["type"])
                ))
        return entities
    
    def get_document_ids_by_entity(self, entity_name: str) -> list[str]:
        """특정 Entity가 언급된 Document ID 목록"""
        doc_ids = []
        with self.driver.session() as session:
            results = session.run(
                cq.GET_DOCUMENT_IDS_BY_ENTITY,
                entity_name=entity_name
            )
            doc_ids = [record["doc_id"] for record in results]
        return doc_ids
    
    def list_all_entities(self, limit: int = 100) -> list[TypedEntity]:
        """전체 Entity 목록 (type별 정렬)"""
        entities = []
        with self.driver.session() as session:
            results = session.run(cq.LIST_ALL_ENTITIES, limit=limit)
            for record in results:
                entities.append(TypedEntity(
                    name=record["name"],
                    type=EntityType(record["type"])
                ))
        return entities
```

---

### Task 3: Application Layer - IngestionService 수정

**파일:** `app/use_cases/ingestion.py`

**변경 내용:**
```python
class IngestionService:
    def __init__(
        self,
        storage: DocumentRepository,
        graph: GraphRepository,  # 추가
        job_repository: JobRepository,
        scraper: ScraperInterface,
        llm: LLMInterface
    ):
        self.graph = graph  # 추가
        # ...
    
    def process_job(self, job_id: str) -> None:
        # ... (기존 로직)
        
        # Document 저장 후 Entity 그래프 구축
        if metadata and metadata.entities:
            self._build_knowledge_graph(doc.id, metadata.entities)
    
    def _build_knowledge_graph(
        self, 
        doc_id: UUID, 
        entities: dict[EntityType, list[str]]
    ) -> None:
        """Entity 노드 및 MENTIONS 관계 생성"""
        for entity_type, names in entities.items():
            for name in names:
                # Entity 노드 생성/조회
                self.graph.save_entity(name, entity_type)
                # MENTIONS 관계 생성
                self.graph.create_mention_relationship(
                    str(doc_id), 
                    name
                )
```

---

### Task 4: API Layer - Entity 엔드포인트 추가

**파일:** `app/interfaces/api/endpoints/entities.py` (신규)

```python
from fastapi import APIRouter, Depends, HTTPException
from app.domain.interfaces.graph_repository import GraphRepository
from app.interfaces.api.dependencies import get_graph_repository

router = APIRouter(prefix="/entities", tags=["entities"])

@router.get("")
async def list_entities(
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    limit: int = 100
):
    """전체 Entity 목록 조회"""
    return graph.list_all_entities(limit=limit)

@router.get("/{name}/documents")
async def get_documents_by_entity(
    name: str,
    graph: Annotated[GraphRepository, Depends(get_graph_repository)],
    storage: Annotated[DocumentRepository, Depends(get_repository)]
):
    """특정 Entity가 언급된 Document 목록"""
    doc_ids = graph.get_document_ids_by_entity(name)
    
    # 실제 Document 조회
    docs = []
    for doc_id in doc_ids:
        doc = storage.get(UUID(doc_id))
        if doc:
            docs.append(doc)
    
    return docs

@router.get("/{name}/info")
async def get_entity_info(
    name: str,
    graph: Annotated[GraphRepository, Depends(get_graph_repository)]
):
    """Entity 정보 및 관련 stats"""
    doc_ids = graph.get_document_ids_by_entity(name)
    
    return {
        "name": name,
        "mention_count": len(doc_ids),
        "documents": doc_ids
    }
```

**main.py 수정:**
```python
from app.interfaces.api.endpoints.entities import router as entities_router

app.include_router(entities_router)
```

---

### Task 5: Dependency Injection - GraphRepository 추가

**파일:** `app/interfaces/api/dependencies.py`

```python
from app.infrastructure.storage.neo4j_graph import Neo4jGraphRepository

_graph_repository_instance = None

def get_graph_repository() -> GraphRepository:
    """Get Neo4jGraphRepository instance"""
    global _graph_repository_instance
    if _graph_repository_instance is None:
        driver = # Neo4j driver (기존)
        _graph_repository_instance = Neo4jGraphRepository(driver)
    return _graph_repository_instance

def get_ingestion_service() -> IngestionService:
    """수정: GraphRepository 주입"""
    return IngestionService(
        storage=get_repository(),
        graph=get_graph_repository(),  # 추가
        job_repository=get_job_repository(),
        scraper=get_scraper(),
        llm=get_llm()
    )
```

---

## ✅ Verification Plan

### 1. Unit Tests

**파일:** `tests/unit/test_neo4j_graph_repository.py` (신규)

```bash
# 실행 명령어
uv run pytest tests/unit/test_neo4j_graph_repository.py -v
```

**테스트 내용:**
- `test_save_entity_creates_node`: Entity 노드 생성 검증
- `test_save_entity_merge_duplicates`: 중복 Entity MERGE 검증
- `test_create_mention_relationship`: MENTIONS 관계 생성 검증
- `test_get_entities_by_document`: Document 기반 Entity 조회
- `test_get_document_ids_by_entity`: Entity 기반 Document 조회

### 2. Integration Tests (BDD)

**파일:** `tests/integration/bdd/test_knowledge_graph.py` (신규)

```bash
# 실행 명령어 (Docker Compose 필요)
docker compose up -d
uv run pytest tests/integration/bdd/test_knowledge_graph.py -v -m integration
```

**시나리오:**
1. **성공: Entity 그래프 자동 구축**
   - Given: 웹 페이지 수집 요청
   - When: LLM이 Entity 추출하고 Document 저장
   - Then: Entity 노드 및 MENTIONS 관계가 자동 생성됨

2. **성공: Entity 기반 Document 검색**
   - Given: 특정 Entity가 여러 Document에 언급됨
   - When: `GET /entities/{name}/documents` 요청
   - Then: 해당 Entity가 언급된 모든 Document 반환

3. **성공: Entity 중복 처리**
   - Given: 두 개의 Document가 동일 Entity 언급
   - When: 두 Document 저장
   - Then: Entity 노드는 하나만 생성되고, MENTIONS 관계는 2개 생성됨

### 3. Contract Tests

**파일:** `tests/contracts/test_graph_repository_contract.py` (신규)

```bash
# 실행 명령어
uv run pytest tests/contracts/test_graph_repository_contract.py -v
```

**테스트 내용:**
- `GraphRepository` 인터페이스 메서드 시그니처 검증
- `Neo4jGraphRepository`가 Protocol 준수 확인

### 4. Manual Testing (선택)

```bash
# 1. 서버 실행
docker compose up -d
uv run uvicorn app.interfaces.api.main:app --reload

# 2. API 테스트
# Document 수집 (Entity 자동 생성)
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html", "enable_extraction": true}'

# Entity 목록 조회
curl "http://localhost:8000/entities"

# 특정 Entity의 Document 조회
curl "http://localhost:8000/entities/[entity_name]/documents"
```

---

## 📦 File Changes Summary

### 신규 파일
- `app/domain/interfaces/graph_repository.py`
- `app/infrastructure/storage/cypher_queries.py` - Cypher 쿼리 템플릿
- `app/infrastructure/storage/neo4j_graph.py`
- `app/interfaces/api/endpoints/entities.py`
- `tests/unit/test_neo4j_graph_repository.py`
- `tests/integration/bdd/test_knowledge_graph.py`
- `tests/contracts/test_graph_repository_contract.py`

### 수정 파일
- `app/use_cases/ingestion.py` - GraphRepository 주입 및 Entity 그래프 구축 로직
- `app/interfaces/api/dependencies.py` - GraphRepository DI
- `app/interfaces/api/main.py` - entities router 추가

---

## ⚠️ Breaking Changes

**없음** - 기존 기능에 영향 없이 추가만 수행

---

## 📝 Migration Notes

기존 Document의 Entity를 Graph로 마이그레이션하려면:

```python
# scripts/migrate_entities_to_graph.py (선택사항)
def migrate():
    docs = storage.list_documents(limit=1000)
    for doc in docs:
        # metadata에서 entities_json 파싱
        if "entities_json" in doc.metadata:
            entities = json.loads(doc.metadata["entities_json"])
            # Graph 구축
            service._build_knowledge_graph(doc.id, entities)
```

---

## 🎯 Success Criteria

1. ✅ Entity 노드가 Neo4j에 생성됨
2. ✅ Document-Entity MENTIONS 관계 생성됨
3. ✅ `GET /entities` API 동작
4. ✅ `GET /entities/{name}/documents` API 동작
5. ✅ Integration Tests 통과 (BDD 시나리오)
6. ✅ Contract Tests 통과
7. ✅ 기존 Document 저장/조회 기능 정상 동작
