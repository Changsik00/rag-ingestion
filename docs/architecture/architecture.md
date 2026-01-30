# Architecture: Clean Architecture (4-Layer)

본 프로젝트는 **Clean Architecture**의 4계층 구조를 엄격히 준수하여 구축되었습니다.

## 🎯 Core Principles

### 1. The Dependency Rule
**의존성은 항상 외부에서 내부(Domain)로만 향한다.**

```
Interfaces → Application → Domain ← Infrastructure
     ↓            ↓            ↑             ↑
   (UI)      (Use Cases)  (Business)    (Technical)
```

- **Domain Layer**: 어떤 외부 레이어도 import하지 않음
- **Application Layer**: Domain만 import
- **Infrastructure Layer**: Domain interfaces만 import (구현체 제공)
- **Interfaces Layer**: Application과 Infrastructure를 조합하여 외부에 노출

### 2. Domain Isolation
비즈니스 로직은 프레임워크, DB, 외부 라이브러리로부터 완전히 격리됩니다.
- LangChain, FastAPI, Neo4j 같은 기술은 Infrastructure Layer에만 존재
- Domain은 순수 Python과 자체 정의 Protocol만 사용

### 3. Protocol-Based Abstraction
구체적 구현체 대신 Protocol(인터페이스)에 의존합니다.
- `LangChainLLMAdapter` 대신 `LLMInterface` Protocol 사용
- `Neo4jStorage` 대신 `DocumentRepository` Protocol 사용

---

## 📂 4-Layer Structure

```
┌─────────────────────────────────────────────────────────┐
│  Interfaces Layer (Presentation)                       │
│  - FastAPI routes, Streamlit UI, CLI                   │
│  - 외부 요청을 Application Layer로 전달                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Application Layer (Use Cases / Orchestration)         │
│  - Ingestion, RAG, AdminAgent                          │
│  - Domain Services를 조합하여 비즈니스 워크플로우 구현   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Domain Layer (Business Logic)                         │
│  - Entities, Value Objects, Domain Services            │
│  - Repository/LLM Protocols (interfaces)               │
│  - 순수 비즈니스 규칙, 외부 의존성 없음                 │
└─────────────────────────────────────────────────────────┘
                          ↑
┌─────────────────────────────────────────────────────────┐
│  Infrastructure Layer (Technical Details)              │
│  - Neo4j, ChromaDB, LangChain adapters                 │
│  - Scrapers, File processors                           │
│  - Domain의 Protocol 구현체 제공                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂 Directory Mapping

### Interfaces Layer (`app/interfaces/`)
외부 세계와의 통신 담당

```
interfaces/
├── api/                    # FastAPI REST API
│   ├── main.py            # Application entry point
│   ├── dependencies.py    # DI Container
│   ├── endpoints/         # Route handlers
│   └── schemas/           # API DTOs (request/response)
└── mcp/                   # MCP Server interface
```

**역할**: HTTP 요청 파싱, 응답 직렬화, Application Layer 호출

---

### Application Layer (`app/application/`)
유스케이스 구현 및 도메인 오케스트레이션

```
application/
└── services/
    ├── ingestion.py        # Ingestion (파일 수집 워크플로우)
    ├── rag.py              # RAG (검색 및 생성 워크플로우)
    ├── admin_agent.py      # AdminAgent (대화형 RAG)
    ├── integrity_service.py # IntegrityService (무결성 검증)
    └── semantic_extractor.py # SemanticExtractor (의미 추출)
```

**역할**: 
- Domain Services를 조합하여 완전한 비즈니스 프로세스 구현
- 트랜잭션 관리, 에러 핸들링
- Infrastructure 구현체 사용 (DI로 주입받음)

**특징**:
- `IngestionService` → `Ingestion` (Service suffix 제거)
- `RAGService` → `RAG`
- Any 타입을 Protocol로 교체 (`DocumentRepository`, `LLMInterface`)

---

### Domain Layer (`app/domain/`)
순수 비즈니스 로직, 외부 의존성 없음

```
domain/
├── entities/               # 식별자(ID) 기반 객체
│   ├── document.py        # Document, Chunk
│   └── job.py             # IngestionJob
│
├── value_objects/          # 값 기반 불변 객체
│   ├── extracted_metadata.py  # ExtractedMetadata
│   ├── intent.py              # UserIntent, IntentType
│   └── ontology.py            # EntityType, RelationshipType
│
├── services/               # Domain Services (상태 없는 비즈니스 로직)
│   ├── intent_classifier.py  # 의도 분류
│   ├── query_rewriter.py     # 쿼리 재작성
│   ├── chunker.py            # 청킹 추상화
│   ├── feedback_service.py   # 피드백 처리
│   └── file_processor.py     # 파일 처리
│
├── interfaces/             # Protocols (Port 정의)
│   ├── document_repository.py # DocumentRepository Protocol
│   ├── graph_repository.py    # GraphRepository Protocol
│   ├── job_repository.py      # JobRepository Protocol
│   ├── scraper.py             # ScraperInterface Protocol
│   ├── llm.py                 # (Legacy LLM Protocol)
│   └── llm_interface.py       # LLMInterface Protocol
│
├── ingestion/              # Ingestion 도메인 모델
│   └── state.py           # IngestionState (LangGraph)
│
└── rag/                    # RAG 도메인 모델
    └── state.py           # RAGState (LangGraph)
```

**핵심 규칙**:
- ❌ `from app.infrastructure` 금지
- ❌ `from langchain`, `from neo4j` 금지
- ✅ `from app.domain.interfaces` (자신의 Protocol만 사용)
- ✅ 순수 Python + Pydantic만 사용

---

### Infrastructure Layer (`app/infrastructure/`)
기술적 구현체, Domain Protocol 구현

```
infrastructure/
├── storage/                # Repository 구현체
│   ├── neo4j_document_repository.py   # DocumentRepository 구현
│   ├── neo4j_graph_repository.py      # GraphRepository 구현
│   ├── neo4j_job_repository.py        # JobRepository 구현
│   ├── chroma.py                       # Vector storage
│   └── composite.py                    # Composite pattern
│
├── llm/                    # LLM Adapter 구현
│   └── langchain_adapter.py  # LLMInterface 구현체
│
├── scrapers/               # Scraper 구현체
│   ├── composite_scraper.py
│   ├── trafilatura_scraper.py
│   ├── playwright_scraper.py
│   └── ...
│
├── chunker/                # Chunker 구현체
│   └── langchain_chunker.py
│
├── brain/                  # LangGraph Workflow
│   └── adapter.py         # LangGraphAdapter
│
├── rag/                    # RAG Graph 구현
│   ├── nodes.py           # RAG Nodes
│   └── graph.py           # RAG Graph Builder
│
└── factories/              # Factory Pattern
    └── llm_factory.py     # LLMFactory
```

**역할**:
- Domain의 Protocol을 실제로 구현
- 외부 라이브러리(LangChain, Neo4j, ChromaDB) 사용
- 기술적 세부 사항 캡슐화

---

## 🔗 Dependency Flow Example

### ❌ Before (잘못된 의존성)
```python
# app/domain/services/storage_integrity_service.py
from app.infrastructure.storage.neo4j import RAGNodes  # ❌ VIOLATION!

class StorageIntegrityService:
    def __init__(self):
        self.nodes = RAGNodes()  # Domain → Infrastructure 의존
```

### ✅ After (올바른 의존성)
```python
# app/domain/interfaces/document_repository.py
class DocumentRepository(Protocol):
    def get_chunks(self, doc_id: str) -> list[Chunk]: ...

# app/application/services/integrity_service.py
from app.domain.interfaces.document_repository import DocumentRepository

class IntegrityService:
    def __init__(self, primary_repo: DocumentRepository, target_repo: DocumentRepository):
        self.primary_repo = primary_repo  # Protocol에만 의존
        self.target_repo = target_repo

# app/interfaces/api/dependencies.py (DI Container)
from app.infrastructure.storage.neo4j_document_repository import Neo4jStorage

def get_storage_integrity_service(...) -> IntegrityService:
    primary_repo = Neo4jStorage(driver)  # 구현체 주입
    return IntegrityService(primary_repo, chroma_storage)
```

---

## 📋 Design Decisions

### 1. Service Suffix 제거
**Before**: `IngestionService`, `RAGService`, `ChunkerService`  
**After**: `Ingestion`, `RAG`, `Chunker`

**이유**: Application Layer의 클래스는 이미 services 폴더 안에 있으므로 suffix 불필요

### 2. Schemas → Value Objects
**Before**: `app/domain/schemas/extraction.py`  
**After**: `app/domain/value_objects/extracted_metadata.py`

**이유**: Clean Architecture에서 "Schema"는 주로 DTO를 의미. 도메인 개념은 Value Object가 더 정확

### 3. Use Cases → Application Services
**Before**: `app/use_cases/ingestion.py`  
**After**: `app/application/services/ingestion.py`

**이유**: "Use Cases"와 "Application Services"는 같은 개념. 일관성을 위해 Application Layer로 통합

### 4. Protocol 기반 타입 시스템
**Before**: `def __init__(self, repo: Any)`  
**After**: `def __init__(self, repo: DocumentRepository)`

**이유**: 
- 명시적 계약 정의
- IDE 자동완성 지원
- 타입 안정성 향상
- 테스트 Mock 작성 용이

---

## 🧪 Testing Strategy

### 계층별 테스트 접근

**Domain Layer** (Unit Tests)
- 외부 의존성 없음 → Mock 불필요
- 순수 비즈니스 로직 검증
- 가장 빠르고 안정적

**Application Layer** (Integration Tests)
- Domain + Infrastructure Mock 조합
- 프로세스 흐름 검증
- Repository/LLM Mock 주입

**Infrastructure Layer** (Integration Tests)
- 실제 DB/External API 사용
- Docker Compose로 격리된 환경
- 느리지만 실제 동작 보장

**Interfaces Layer** (E2E Tests)
- FastAPI TestClient 사용
- 전체 시스템 통합 검증

---

## 🚀 Benefits

### 1. 테스트 용이성
- Domain은 Mock 없이 테스트
- Infrastructure는 쉽게 교체 가능

### 2. 유지보수성
- 계층 간 명확한 경계
- 변경 영향 범위 최소화

### 3. 확장성
- 새 Repository 추가 → Infrastructure만 수정
- 새 API 추가 → Interfaces만 수정
- Business Rule 변경 → Domain만 수정

### 4. 기술 독립성
- LangChain → LlamaIndex 교체 가능
- FastAPI → Django 교체 가능
- Neo4j → PostgreSQL 교체 가능

---

## 📚 References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Python Protocol (PEP 544)](https://peps.python.org/pep-0544/)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

---

**Last Updated**: 2026-01-31 (Spec 050 - Clean Architecture Refactoring)
