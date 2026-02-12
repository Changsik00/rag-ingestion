# Spec-076: Ingestion Transaction Integrity (Saga Pattern)

## 📋 배경 및 문제 정의 (Background & Problem)

### 현재 상황
현재 시스템은 절차적(Procedural) 방식으로 문서 수집 파이프라인이 구현되어 있습니다. 스크래핑, 중복 체크, 메타데이터 추출, 청킹, 인덱싱 단계가 순차적으로 실행되며, 중간 단계에서 실패가 발생할 경우 이전 단계에서 생성된 데이터가 남게 됩니다.

### 문제점
- **데이터 불일치**: 인덱싱 단계에서 실패하면 Neo4j에는 데이터가 저장되었으나 ChromaDB에는 반영되지 않거나, 그 반대의 상황이 발생하여 RAG 엔진의 신뢰성을 떨어뜨립니다.
- **리소스 낭비**: 실패한 작업의 부산물(문서, 청크)들이 DB에 잔류하여 인프라 비용을 증가시킵니다.
- **수동 복구**: 부분 실패 시 관리자가 일일이 DB를 점검하고 삭제해야 하는 번거로움이 있습니다.

### 해결 방안
**Choreography 기반 Saga 패턴**을 도입하여 각 수집 단계 간의 트랜잭션 무결성을 보장합니다.
- 내부 이벤트 버스를 통한 비동기 이벤트 전달.
- 각 서비스는 이전 단계의 성공 이벤트를 구독하여 다음 작업을 수행.
- 실패 이벤트 발생 시 **보상 트랜잭션(Compensating Transaction)**을 실행하여 이미 반영된 데이터를 삭제(Undo)함으로써 원자성(Atomicity)을 확보합니다.

## 📊 개념도 (Conceptual Architecture)
```mermaid
graph TD
    Start([Ingestion Started]) --> Collection[Collection Service]
    Collection -- Success -->|ContentCollected| Deduplication[Deduplication Service]
    Deduplication -- Success -->|ContentUnique| Extraction[Extraction Service]
    Extraction -- Success -->|MetadataExtracted| Chunking[Chunking Service]
    Chunking -- Success -->|DocumentChunked| Indexing[Indexing Service]
    Indexing -- Success -->|DataIndexed| End([Ingestion Completed])

    Indexing -- Failure --> Rollback[Rollback Handler]
    Extraction -- Failure --> Rollback
    Rollback -->|Compensate| UndoIndexing[Delete From Chroma/Neo4j]
    Rollback -->|Compensate| UndoCollection[Cleanup Temp Files]
```

## 🎯 요구사항 (Requirements)

### Functional Requirements
1. **내부 이벤트 버스**: `asyncio`를 활용한 프로세스 내 이벤트 발행/구독 모델 구현.
2. **도메인 이벤트 정의**: 각 수집 단계의 상태 변화를 나타내는 명확한 이벤트 클래스 도입.
3. **보상 트랜잭션 구현**: 인코딩/인덱싱 실패 시 Neo4j 및 ChromaDB에서 특정 문서를 삭제하는 기능 구현.
4. **상태 관리**: `JobStatus`를 세분화하여 현재 Saga가 어떤 단계에 있는지 추적 가능하도록 함.

### Non-Functional Requirements
1. **Idempotency**: 보상 트랜잭션은 여러 번 실행되어도 안전해야 함 (데이터가 이미 없으면 통과).
2. **Performance Impact**: 이벤트 기반 전환으로 인한 지연 시간(Latency) 증가를 최소화함.

## ✅ Definition of Done
1. **통합 테스트 통과**: 인덱싱 단계에서 의도적으로 에러를 발생시켰을 때, Neo4j와 ChromaDB에서 데이터가 깨끗하게 삭제됨을 확인.
2. **이벤트 로그**: 각 단계별 이벤트 발행 및 수신 로그가 정확히 남음.
3. **문서화**: 새로운 수집 흐름과 이벤트 정의에 대한 기술 문서 업데이트.
4. **Test Coverage**: Saga 핸들러 및 롤백 로직에 대한 테스트 커버리지 80% 이상 확보.
