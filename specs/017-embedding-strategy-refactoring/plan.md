# Implementation Plan: Spec 017 - Embedding Strategy Refactoring

## 📋 개요

ChromaDB의 로컬 embedding 모델을 Gemini Embedding API로 전환하여 Heavy ML dependencies를 제거하고, 4개의 실패하는 integration test를 수정합니다.

---

## 🎯 목표

1. **Primary Goal**: ChromaDB embedding을 Gemini API 기반으로 전환
2. **Test Fix**: 4개 실패 테스트 모두 통과
3. **Dependency Cleanup**: `onnxruntime`, `tokenizers` 제거

---

## 📝 구현 계획

### Task 1: 브랜치 생성 및 현재 테스트 상태 확인

**브랜치 전략**:
```bash
git checkout -b feature/017-embedding-strategy-refactoring
```

**테스트 실행**:
```bash
uv run pytest -v tests/integration/bdd/test_knowledge_graph.py::test_successful_entity_graph_auto_construction
uv run pytest -v tests/integration/bdd/test_knowledge_graph.py::test_entity_based_document_search
uv run pytest -v tests/integration/bdd/test_knowledge_graph.py::test_entity_deduplication
uv run pytest -v tests/integration/bdd/test_high_priority_scenarios.py::test_duplicate_url_sequential_ingestion
```

**Expected**: 모두 FAILED (embedding 이슈)

---

### Task 2: ChromaDB Embedding 설정 변경

**파일**: `app/infrastructure/storage/chroma.py`

**변경 사항**:
1. `GoogleGenerativeAIEmbeddings` import 추가
2. `ChromaStorage.__init__()` 메서드 수정:
   - Gemini embedding function 생성
   - `get_or_create_collection()` 호출 시 `embedding_function` 전달

**구현 예시**:
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class ChromaStorage(DocumentRepository):
    def __init__(self):
        host = os.getenv("CHROMA_HOST", "localhost")
        port = os.getenv("CHROMA_PORT", "8001")
        self.client = chromadb.HttpClient(host=host, port=int(port))
        
        # Gemini Embedding Function 설정
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=gemini_api_key
        )
        
        self.collection = self.client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_function
        )
```

**TDD**:
- **Test**: `tests/unit/test_storage.py`에서 ChromaStorage 초기화 테스트 확인
- **Expected**: Embedding function이 올바르게 설정됨

**커밋**:
```
refactor(spec-017): integrate gemini embedding api with chromadb

- Replace local all-MiniLM-L6-v2 with Gemini text-embedding-004
- Add embedding_function to ChromaStorage initialization
- Require GEMINI_API_KEY environment variable
```

---

### Task 3: 의존성 제거

**파일**: `pyproject.toml`

**변경 사항**:
```diff
dependencies = [
    "beautifulsoup4>=4.14.3",
    "fastapi>=0.128.0",
    # ... other dependencies
-   "onnxruntime>=1.16.0",
-   "tokenizers>=0.15.0",
]
```

**Verification**:
```bash
uv lock
uv sync
```

**커밋**:
```
chore(spec-017): remove heavy ml dependencies

- Remove onnxruntime (no longer needed)
- Remove tokenizers (no longer needed)
- ChromaDB now uses Gemini Embedding API
```

---

### Task 4: Integration Test 실행 및 수정

**테스트 실행**:
```bash
# Docker Compose 환경 시작
docker-compose up -d

# 4개 실패 테스트 실행
uv run pytest -v tests/integration/bdd/ -k "test_successful_entity_graph_auto_construction or test_entity_based_document_search or test_entity_deduplication or test_duplicate_url_sequential_ingestion"
```

**예상 시나리오**:
1. **성공**: Embedding이 정상 작동하여 테스트 통과
2. **실패 (환경변수 누락)**: `.env`에 `GEMINI_API_KEY` 추가 필요
3. **실패 (API 이슈)**: Gemini API 호출 문제 디버깅

**수정 계획**:
- 실패 원인에 따라 코드 또는 환경설정 수정
- 로깅 추가하여 embedding 과정 디버깅

**커밋** (필요 시):
```
fix(spec-017): resolve gemini embedding integration issues

- Add proper error handling for API calls
- Improve logging for embedding process
```

---

### Task 5: 전체 테스트 스위트 실행

**테스트 실행**:
```bash
uv run pytest -v
```

**Expected**: 
- 4개 이전 실패 테스트 → PASSED
- 기존 통과 테스트 → 여전히 PASSED (회귀 없음)

**회귀 발생 시**:
- 문제 분석 및 수정
- 추가 커밋

---

### Task 6: Docker 환경 검증

**Docker 빌드 및 실행**:
```bash
docker-compose down -v
docker-compose build
docker-compose up -d
```

**API 테스트**:
```bash
# Health check
curl http://localhost:8000/docs

# Integration test 재실행
uv run pytest -v tests/integration/bdd/
```

**Expected**: Docker 환경에서도 모든 테스트 통과

---

### Task 7: 백로그 업데이트

**파일**: `backlog/queue.md`

**변경 사항**:
- Spec 017을 Phase 3에 추가
- 상태를 `[x]` (완료)로 표시
- Note에 수정된 테스트 목록 추가

**커밋**:
```
docs: mark spec 017 as completed in backlog

- Embedding strategy refactored to Gemini API
- 4 failing integration tests now pass
- Heavy ML dependencies removed
```

---

### Task 8: PR 준비

**파일 생성**:
1. `specs/017-embedding-strategy-refactoring/walkthrough.md`
2. `specs/017-embedding-strategy-refactoring/pr_description.md`

**PR 생성**:
```bash
git push origin feature/017-embedding-strategy-refactoring

gh pr create \
  --base main \
  --head feature/017-embedding-strategy-refactoring \
  --title "refactor(spec-017): embedding strategy refactoring" \
  --body-file specs/017-embedding-strategy-refactoring/pr_description.md
```

---

## 🧪 검증 계획

### Automated Tests

**Unit Tests**:
```bash
uv run pytest tests/unit/test_storage.py -v
```
- ChromaStorage 초기화 테스트
- Embedding function 설정 검증

**Integration Tests**:
```bash
uv run pytest tests/integration/bdd/ -v
```
- 4개 이전 실패 테스트 모두 통과 확인
- 기존 통과 테스트 회귀 없음 확인

**Full Test Suite**:
```bash
uv run pytest -v
```
- 전체 테스트 스위트 통과

### Manual Verification

**Docker 환경 테스트**:
1. Docker Compose로 전체 환경 시작
2. Swagger UI에서 `/ingest/web` 엔드포인트 테스트
3. Entity 추출 및 저장 확인
4. ChromaDB에 embedding이 정상적으로 저장되는지 확인

**의존성 검증**:
```bash
uv tree | grep -E "(onnxruntime|tokenizers)"
```
- 결과가 비어있어야 함 (완전히 제거 확인)

**Docker 이미지 크기 비교**:
```bash
docker images | grep rag-ingestion
```
- 이전 이미지 크기와 비교하여 감소 확인

---

## 🚨 리스크 및 대응

### Risk 1: Gemini API Rate Limit
**대응**: Free tier 한도 확인 및 필요 시 API 호출 최적화

### Risk 2: Embedding 품질 저하
**대응**: 테스트 결과 비교 및 필요 시 다른 Gemini embedding model 테스트 (text-embedding-005 등)

### Risk 3: 환경변수 관리
**대응**: `.env.example` 업데이트 및 문서화

---

## 📚 참고 자료

- [ChromaDB Embedding Functions](https://docs.trychroma.com/embeddings)
- [LangChain Google GenAI Integration](https://python.langchain.com/docs/integrations/text_embedding/google_generative_ai)
- [Gemini Embedding Models](https://ai.google.dev/gemini-api/docs/embeddings)
