# Spec 002 Walkthrough: Atomic Storage & Swagger Admin

## 1. Overview
수집된 데이터를 영구 저장하기 위해 **Graph DB (Neo4j)**와 **Vector DB (Chroma)**를 도입했습니다.
또한 **DDD(Domain-Driven Design)** 전술적 패턴을 적용하여 도메인 모델을 더욱 견고하게 리팩토링했습니다.

## 2. Architecture Changes (Refactoring)
`docs/architecture.md`에 정의된 대로 구조를 개선했습니다.
- **Domain Layer**:
    - `entities/`: `AtomicDocument` (ID, Lifecycle)
    - `value_objects/`: `Source` (Immutable URL)
    - `interfaces/`: `DocumentRepository` (Abstract)
- **Infrastructure Layer**:
    - `storage/`: `Neo4jStorage`, `ChromaStorage`, `CompositeStorage`

## 3. Implementation Details

### Composite Storage Pattern
두 개의 이기종 DB(Graph + Vector)를 하나의 트랜잭션처럼 다루기 위해 `CompositeStorage`를 도입했습니다. UseCase는 이것이 2개의 DB인지 알 필요가 없습니다.

```python
class CompositeStorage(DocumentRepository):
    def save(self, document):
        self.neo4j.save(document)  # 구조/메타데이터 저장
        self.chroma.save(document) # 임베딩 저장
```

### Dependency Injection
`main.py`에서 `CompositeStorage`를 조립하여 주입합니다.

## 4. Verification Result

### ✅ Automated Tests
- **Unit Tests**: `CompositeStorage`가 두 하위 저장소를 올바르게 호출하는지 Mock으로 검증.
- **Integration Tests**: API 레벨에서 Repository를 Mocking하여 Controller 로직(POST/GET) 검증 완료.

```bash
tests/unit/test_storage.py ..                                          [ 50%]
tests/integration/test_api_ingest.py ..                                [100%]
```

## 5. Next Steps
- `backlog/queue.md` 업데이트 (Spec 002 완료)
- Admin Dashboard (Streamlit) 구현 준비
