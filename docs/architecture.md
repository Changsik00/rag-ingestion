# Project Architecture: Clean Architecture + DDD

본 프로젝트는 **Clean Architecture**의 계층 구조 원칙 위에 **Domain-Driven Design (DDD)** 의 전술적 패턴을 적용하여 구축됩니다.

## 🎯 Core Philosophy
1.  **Dependency Rule**: 의존성은 항상 외부에서 내부(Domain)로 향해야 한다.
2.  **Domain Isolation**: 비즈니스 로직은 프레임워크나 DB로부터 완전히 격리되어야 한다.
3.  **Explicit Intent**: 코드를 봤을 때 "무엇을 하는지"가 기술적 구현보다 먼저 보여야 한다.

## 📂 Directory Structure (Updated)

```plaintext
rag-ingestion/
├── app/
│   ├── core/               # 설정 및 공통 Utilities (LLM Factory 등)
│   │
│   ├── domain/             # [Core] 순수 비즈니스 로직, 외부 의존성 0%
│   │   ├── entities/       # 식별자(ID)가 있고 생명주기를 가지는 객체 (e.g., Document, Job)
│   │   ├── value_objects/  # 식별자가 없고 값 그 자체로 의미를 가지는 객체 (e.g., Source)
│   │   ├── schemas/        # 도메인 데이터 구조 (e.g., ExtractedMetadata)
│   │   ├── services/       # 도메인 서비스 (e.g., SemanticExtractor)
│   │   └── interfaces/     # Repository 및 외부 서비스에 대한 추상체 (Port)
│   │       ├── llm.py          # ← NEW! LLM Protocol 인터페이스
│   │       ├── document_repository.py
│   │       ├── job_repository.py
│   │       └── scraper.py
│   │
│   ├── use_cases/          # [Application] 도메인 객체를 오케스트레이션
│   │   └── ingestion.py    # "수집하여 저장한다"와 같은 유스케이스 흐름 제어
│   │
│   ├── infrastructure/     # [Adapter] 도메인 인터페이스의 실제 구현체
│   │   ├── storage/        # DB 구현체 (Neo4j, Chroma, LocalFile 등)
│   │   ├── scrapers/       # 웹 스크래핑 구현체 (BeautifulSoup, Firecrawl)
│   │   └── llm/            # ← NEW! LLM Adapter 구현체
│   │       └── langchain_adapter.py  # LangChain을 LLMInterface로 변환
│   │
│   └── interfaces/         # [Presentation/Driver] 시스템 진입점
│       ├── api/            # FastAPI 라우터 및 스키마
│       │   ├── dependencies.py  # DI 컨테이너
│       │   └── main.py
│       └── cli/            # CLI 커맨드
```

## 🏗 Design Decisions & Rationale

### 1. 왜 `Entities`와 `Value Objects`를 나누는가?
-   **Why**: 데이터의 성격을 명확히 하기 위함입니다.
-   **Entity (`AtomicDocument`, `IngestionJob`)**: 내용이 변해도 ID가 같으면 같은 객체입니다. DB에 저장되고 관리 대상이 됩니다.
-   **Value Object (`Source`)**: URL이 바뀌면 아예 다른 객체입니다. 불변(Immutable)성을 가지며 사이드 이펙트를 줄여줍니다.

### 2. 왜 `DB` 대신 `Storage`인가?
-   **Why**: 기술 종속성을 피하기 위함입니다.
-   `DB`라고 하면 자꾸 RDBMS나 SQL을 떠올리게 됩니다. 도메인 입장에서 중요한 건 "저장한다"는 행위이지, 그것이 SQL인지 Graph인지 파일인지는 중요하지 않습니다.

### 3. Repository Pattern은 왜 필수인가?
-   **Why**: 테스트와 교체를 자유롭게 하기 위함입니다.
-   `app/domain/interfaces/document_repository.py`만 보고 개발하면, 실제 DB가 없어도 `MemoryRepository`로 테스트를 짤 수 있습니다. (Fast Test Loop)

### 4. `interfaces/api/main.py` 위치 선정 이유
-   **Why**: 프레임워크도 "세부 사항"이기 때문입니다.
-   Django나 FastAPI 같은 웹 프레임워크는 도메인의 주인이 아닙니다. 도메인을 외부에 노출시키는 '인터페이스'일 뿐입니다. 따라서 `app/` 최상단이 아닌 `interfaces/api/`에 위치시킵니다.

### 5. **NEW! Protocol 패턴을 활용한 추상화 (Spec 006)**

-   **Why**: Domain을 외부 프레임워크로부터 완전히 격리하기 위함입니다.
-   **Before (Spec 005)**: Domain에서 LangChain을 직접 사용 → 프레임워크 교체 시 Domain 수정 필요
-   **After (Spec 006)**: Domain은 `LLMInterface` Protocol만 의존 → Infrastructure에서 구현체 교체 가능

**예시: LLM 인터페이스**
```python
# domain/interfaces/llm.py (Protocol)
from typing import Protocol
class LLMInterface(Protocol):
    def extract_metadata(self, text: str) -> Optional[ExtractedMetadata]:
        ...

# infrastructure/llm/langchain_adapter.py (Adapter)
class LangChainLLMAdapter:
    def extract_metadata(self, text: str):
        return self.chain.invoke({"text": text})
```

**장점**:
- ✅ LangChain → OpenAI/Claude로 교체 시 Domain 수정 불필요
- ✅ 테스트에서 간단한 Mock 사용 가능
- ✅ Dependency Inversion Principle (DIP) 준수

### 6. 데이터 저장 전략: Job과 Doc의 분리 (Separation of Concerns)

본 프로젝트는 **운영 데이터(Job)**와 **지식 데이터(Doc)**를 구조적으로 분리하여 관리합니다. 이는 두 데이터의 성격과 관리 목적이 근본적으로 다르기 때문입니다.

#### 6.1 저장소 구성 (Where to Store?)
| 데이터 (Data) | 저장소 (Database) | 역할 (Role) |
| :--- | :--- | :--- |
| **Job (작업)** | **Neo4j** | **운영 관리 (Operations)**. 수집 작업의 상태(성공/실패/재시도), 시점, 에러 메시지 등 **Task의 흐름(Flow)**을 그래프로 관리합니다. |
| **Doc (문서)** | **Neo4j** + **ChromaDB** | **지식 저장 (Knowledge)**. 수집된 실제 콘텐츠입니다. <br> - **Neo4j**: 문서의 메타데이터, 구조, 다른 문서와의 관계 (Ontology). <br> - **ChromaDB**: 텍스트의 벡터 임베딩 (Vector Embedding)을 저장하여 의미 기반 검색(RAG)을 지원합니다. |

#### 6.2 분리 저장의 이유 (Rationale)
1.  **관점의 차이 (Process vs Product)**
    -   **Job**은 "어떻게(How) 가져왔는가?"에 대한 **과정(Process)**의 기록입니다.
    -   **Doc**은 "무엇을(What) 가져왔는가?"에 대한 **결과물(Product)**입니다.
    -   수집 작업이 실패하더라도(Job Fail), 이전에 수집된 문서는 검색되어야 하며, 반대로 문서를 삭제해도 감사(Audit)를 위해 수집 이력은 남아야 합니다.
2.  **하이브리드 스토리지 (Hybrid Storage Strategy)**
    -   Job은 작업 간의 선후 관계, 재시도 트리(`retry_of`) 등 **관계(Relationship)**가 중요하므로 Graph DB가 적합합니다.
    -   Doc은 구조적 관계(Graph)와 의미적 유사도(Vector)가 모두 필요하므로, **Composite Storage Pattern**을 적용하여 각 DB의 장점을 극대화합니다.

#### 6.3 로드맵: 온톨로지 및 지식 그래프 (Future Roadmap)
현재는 데이터를 "적재(Node Creation)" 및 **기본 메타데이터 추출(Spec 005-006 완료)**을 완료한 상태입니다. 향후 다음과 같이 **관계(Relationship)**를 중심으로 발전합니다.

1.  **Spec 007: Ontology Design**
    -   추출된 Entities를 목적에 맞게 분류하고 관계 스키마를 설계합니다.
2.  **Spec 008: Knowledge Graph Construction**
    -   `(Document)-[:MENTIONS]->(Entity)-[:RELATED_TO]->(Entity)` 관계를 형성합니다.
3.  **Graph RAG**
    -   단순 벡터 검색(Vector Search)의 한계를 넘어, 그래프 관계를 활용한 복합 추론(Reasoning)이 가능한 RAG 시스템으로 고도화합니다.

### 4. Architecture Decisions (ADR)
주요 아키텍처 결정 사항은 [docs/architecture_decisions.md](architecture_decisions.md)에 기록합니다.

---

## 🎓 학습 자료

- **Clean Architecture**: Robert C. Martin - "Clean Architecture: A Craftsman's Guide to Software Structure and Design"
- **Protocol Pattern**: [PEP 544 – Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- **DDD**: Eric Evans - "Domain-Driven Design: Tackling Complexity in the Heart of Software"
