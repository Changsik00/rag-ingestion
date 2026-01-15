# Spec 002: Atomic Storage & Swagger Admin

## 1. Background
현재 시스템은 수집된 데이터를 메모리상에서 마크다운으로 변환하여 반환하기만 합니다. RAG 시스템의 핵심은 수집된 지식을 **검색 가능한 형태(Vector/Graph)**로 저장하는 것입니다. 본 스펙에서는 영구 저장소(Persistence)를 도입합니다.

## 2. Requirements

### 2.1 Database Setup
- **Neo4j**: Graph Database. 지식 간의 관계 저장.
- **ChromaDB**: Vector Database. 텍스트 임베딩 저장.
- 개발 편의를 위해 `docker-compose.yml`로 관리해야 함.

### 2.2 Atomic Document Model
- 수집된 하나의 문서는 `AtomicDocument`라는 단위로 관리된다.
- **Attributes**:
    - `id`: UUID
    - `source_url`: 출처 URL
    - `content`: 마크다운 원문
    - `metadata`: HTTP 상태 코드, 수집 시간 등

### 2.3 Ingestion Pipeline Update
- **Input**: URL
- **Process**: Scraping -> Parsing -> **Saving**
- **Output**: 저장된 Document ID 및 상태

### 2.4 Swagger Admin (API)
- 개발자가 데이터를 쉽게 확인할 수 있어야 한다.
- `GET /documents`: 최근 수집된 문서 10개 조회.

## 3. Non-Functional Requirements
- **Clean Architecture 준수**: DB 의존성은 `infrastructure` 레이어에 격리되어야 한다.
- **Testability**: DB 없이도 서비스 로직 테스트가 가능해야 한다 (Interface 활용).
