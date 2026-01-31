# Integration Test Infrastructure Improvement

## Overview

**Status**: Backlog  
**Priority**: Medium  
**Estimated Effort**: 2-3 days  
**Related Spec**: [Spec 050](../050-dependency-rule-enforcement/task.md)

## Problem Statement

현재 integration tests는 **특정 DB 상태를 가정**하고 작성되어 있어, 독립적으로 실행할 수 없습니다:

- ❌ Docker 인프라 켜져있는지 확인 안함
- ❌ 필요한 테스트 데이터가 DB에 있는지 보장 안됨
- ❌ 테스트 간 데이터 격리가 안되어 있음
- ❌ 실행 순서에 의존적 (order-dependent)

### Current Failures
```
16 integration tests failing:
- API tests (2)
- BDD scenarios (8) 
- TDD integration (3)
- Repository tests (3)
```

## Requirements

### 1. Infrastructure Preparation

**Docker Services Check**:
```bash
# Before running tests, verify:
- Neo4j is running (port 7687)
- ChromaDB is running (port 8000)
- PostgreSQL is running (if applicable)
```

**Implementation**:
```python
# conftest.py
@pytest.fixture(scope="session", autouse=True)
def check_infrastructure():
    """Verify all required services are running"""
    services = {
        "neo4j": ("localhost", 7687),
        "chroma": ("localhost", 8000),
    }
    
    for service, (host, port) in services.items():
        if not is_port_open(host, port):
            pytest.skip(f"{service} is not running on {host}:{port}")
```

### 2. Test Data Preparation

**Seed Data Jobs**:
```python
@pytest.fixture(scope="session")
def seed_test_data(check_infrastructure):
    """
    Seed database with required test data
    
    Steps:
    1. Check if test data exists
    2. If not, run ingestion jobs for:
       - Sample Wikipedia article
       - Sample GitHub README
       - Sample PDF document
    3. Wait for completion
    4. Verify data is indexed
    """
    # Implementation here
```

**Test Data Requirements**:
- 최소 3개의 문서 (다양한 소스 타입)
- 각 문서별 청크 데이터 (vector + keyword)
- 엔티티 및 관계 데이터 (graph)

### 3. Scenario-Based Test Structure

**Current Structure** (문제):
```python
def test_rag_autocomplete():
    # Assumes "LangChain" document exists
    response = client.get("/autocomplete?q=Lang")
    assert "LangChain" in response
```

**Proposed Structure** (해결):
```python
class TestRAGWithWikipediaData:
    """
    Scenario: User queries about pre-ingested Wikipedia article
    
    Given: Wikipedia article about "Artificial Intelligence" is ingested
    When: User searches for AI-related topics
    Then: System returns relevant chunks with citations
    """
    
    @pytest.fixture(scope="class")
    def wikipedia_article(self, seed_test_data):
        """Ensure Wikipedia test data is available"""
        return seed_test_data["wikipedia"]["artificial_intelligence"]
    
    def test_autocomplete_suggests_article_title(self, wikipedia_article):
        response = client.get("/autocomplete?q=Artif")
        assert "Artificial Intelligence" in response.json()
    
    def test_rag_returns_wikipedia_chunks(self, wikipedia_article):
        response = client.post("/rag/ask", json={
            "query": "What is AI?",
            "filters": {"source": [wikipedia_article["url"]]}
        })
        assert len(response.json()["chunks"]) > 0
        assert wikipedia_article["url"] in response.json()["citations"]
```

## Proposed Test Scenarios

### Scenario 1: Fresh Start (No Data)
```
1. Start with empty databases
2. Ingest sample document via API
3. Wait for job completion
4. Query the ingested data
5. Verify results
```

### Scenario 2: Multi-Document Query
```
1. Ensure 3+ documents are indexed
2. Query without filters (general query)
3. Verify hybrid retrieval (vector + keyword + graph)
4. Verify citations from multiple sources
```

### Scenario 3: Filtered Search
```
1. Ensure documents from different sources exist
2. Apply source filter
3. Verify only filtered documents are returned
4. Verify fallback if filtered results are empty
```

### Scenario 4: Entity Graph
```
1. Ingest document with named entities
2. Verify entities are extracted and stored in Neo4j
3. Query related entities
4. Verify graph traversal works
```

## Implementation Plan

### Phase 1: Infrastructure Fixtures
- [ ] Create `check_infrastructure()` fixture
- [ ] Create `docker_compose_up()` helper (optional)
- [ ] Add service health checks

### Phase 2: Data Seeding
- [ ] Create `seed_test_data()` fixture
- [ ] Define minimal test dataset (3 documents)
- [ ] Implement data verification
- [ ] Add cleanup after tests (optional)

### Phase 3: Refactor Existing Tests
- [ ] Group tests by scenario
- [ ] Add proper fixtures for data dependencies
- [ ] Remove hardcoded assumptions
- [ ] Add clear docstrings explaining scenario

### Phase 4: Documentation
- [ ] Create `tests/integration/README.md`
- [ ] Document how to run integration tests locally
- [ ] Document required environment setup
- [ ] Add troubleshooting guide

## Sample Test Dataset

### Document 1: Wikipedia - Artificial Intelligence
```yaml
title: "Artificial Intelligence"
url: "https://en.wikipedia.org/wiki/Artificial_Intelligence"
content_length: ~5000 words
entities:
  - John McCarthy (PERSON)
  - Machine Learning (CONCEPT)
  - Stanford University (ORGANIZATION)
chunks: ~20
```

### Document 2: GitHub - LangChain README
```yaml
title: "LangChain"
url: "https://github.com/langchain-ai/langchain"
content_length: ~2000 words
entities:
  - Harrison Chase (PERSON)
  - Python (TECHNOLOGY)
chunks: ~10
```

### Document 3: PDF - Sample Research Paper
```yaml
title: "Attention Is All You Need"
url: "file://tests/fixtures/attention_paper.pdf"
content_length: ~3000 words
entities:
  - Transformer (CONCEPT)
  - Google Brain (ORGANIZATION)
chunks: ~15
```

## Success Criteria

- [ ] ✅ All integration tests can run independently
- [ ] ✅ Tests pass with fresh database
- [ ] ✅ Tests pass when run in any order
- [ ] ✅ Clear error messages when infrastructure is not ready
- [ ] ✅ Test execution time < 2 minutes
- [ ] ✅ Documentation is complete and clear

## Benefits

1. **Reliability**: Tests won't fail due to missing data
2. **Reproducibility**: Same results every time
3. **Developer Experience**: Clear setup instructions
4. **CI/CD Ready**: Can run in automated pipelines
5. **Debugging**: Easier to diagnose failures

## References

- pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
- Docker health checks: https://docs.docker.com/engine/reference/builder/#healthcheck
- Test data factories: https://factoryboy.readthedocs.io/

## Related

- [Spec 050: Clean Architecture Refactoring](../050-dependency-rule-enforcement/task.md)
- Current test failures: 16 integration tests
- Unit test coverage: 100% (232/232 passing)
