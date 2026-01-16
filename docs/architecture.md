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
│   ├── core/               # 설정 및 공통 에러 정의
│   │
│   ├── domain/             # [Core] 순수 비즈니스 로직, 외부 의존성 0%
│   │   ├── entities/       # 식별자(ID)가 있고 생명주기를 가지는 객체 (e.g., Document)
│   │   ├── value_objects/  # 식별자가 없고 값 그 자체로 의미를 가지는 객체 (e.g., Source)
│   │   ├── policies/       # 도메인 규칙 및 제약 조건 (e.g., IngestionPolicy)
│   │   └── interfaces/     # Repository 및 외부 서비스에 대한 추상체 (Port)
│   │
│   ├── use_cases/          # [Application] 도메인 객체를 오케스트레이션
│   │   └── ingestion.py    # "수집하여 저장한다"와 같은 유스케이스 흐름 제어
│   │
│   ├── infrastructure/     # [Adapter] 도메인 인터페이스의 실제 구현체
│   │   ├── storage/        # DB 구현체 (Neo4j, Chroma, LocalFile 등)
│   │   ├── scrapers/       # 웹 스크래핑 구현체 (BeautifulSoup, Firecrawl)
│   │   └── adapters/       # 기타 외부 통신 어댑터 (HTTP Client 등)
│   │
│   └── interfaces/         # [Presentation/Driver] 시스템 진입점
│       ├── api/            # FastAPI 라우터 및 스키마
│       └── cli/            # CLI 커맨드
```

## 🏗 Design Decisions & Rationale

### 1. 왜 `Entities`와 `Value Objects`를 나누는가?
-   **Why**: 데이터의 성격을 명확히 하기 위함입니다.
-   **Entity (`AtomicDocument`)**: 내용이 변해도 ID가 같으면 같은 객체입니다. DB에 저장되고 관리 대상이 됩니다.
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

### 5. 데이터 저장 전략: Job과 Doc의 분리 (Separation of Concerns)
-   **Why**: 운영 데이터(Operations)와 지식 데이터(Knowledge)의 생명주기와 목적이 다르기 때문입니다.
    -   **Job (작업)**: "어떻게(How) 가져왔는가?"에 대한 기록. (**Process**)
    -   **Doc (문서)**: "무엇을(What) 가져왔는가?"에 대한 결과물. (**Product**)
-   **Hybrid Storage 구성**:
    -   **Job → Neo4j**: 작업 흐름, 상태(Status), 재시도 이력(Retry Traceability) 등 **관계 중심**의 데이터이므로 그래프 DB가 적합합니다.
    -   **Doc → Neo4j + ChromaDB**:
        -   **Neo4j**: 문서의 메타데이터, 구조, 지식 그래프(Ontology) 표현.
        -   **ChromaDB**: 의미 기반 검색(Semantic Search)을 위한 벡터 임베딩 저장.
-   **Future Vision**: 향후 `(Job)-[:CREATED]->(Doc)` 관계를 통해 데이터의 출처(Provenance)를 추적하고, 단순 검색을 넘어선 **Graph RAG**로 발전시킬 기반을 마련합니다.
