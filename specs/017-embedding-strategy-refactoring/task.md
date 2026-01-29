# Task List: Spec 017 - Embedding Strategy Refactoring

## Progress

- [x] Spec 번호 확정 (017)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [x] 사용자 승인 완료
- [x] Task 1 완료: 브랜치 생성 및 테스트 상태 확인
- [x] Task 2 완료: ChromaDB Embedding 설정 변경 (Unit tests 통과)
- [x] Task 3 완료: 의존성 제거 (직접 의존성에서 제거)
- [x] Task 4 완료: Integration Test 통과 (4 passed) ✅
- [x] Task 5: 전체 테스트 스위트 실행

---

## Task 1: 브랜치 생성 및 현재 테스트 상태 확인

### 1-1. 브랜치 생성
- [x] 브랜치 생성: `git checkout -b feature/017-embedding-strategy-refactoring`
- [x] 브랜치 확인: `git branch --show-current`

### 1-2. 실패 테스트 확인
- [x] Docker 환경 시작
- [x] 테스트 실행 및 실패 확인 (job status: FAILED)

**결과**: 테스트 실패 확인됨. ChromaDB embedding 이슈로 인해 ingestion job이 FAILED 상태로 완료됨.

**커밋 메시지**:
```
docs: add spec 017 - embedding strategy refactoring

- Add embedding refactoring spec
- Document ChromaDB embedding issues  
- Plan migration to Gemini Embedding API
- Update backlog with Spec 017
```
✅ 커밋 완료: ce06b64

---

## Task 2: ChromaDB Embedding 설정 변경

### 2-1. chroma.py 수정
- [x] Import 추가: `from langchain_google_genai import GoogleGenerativeAIEmbeddings`
- [x] `ChromaStorage.__init__()` 수정:
  - [x] GEMINI_API_KEY 환경변수 확인
  - [x] GoogleGenerativeAIEmbeddings 인스턴스 생성
  - [x] `get_or_create_collection()` 호출 시 `embedding_function` 전달

### 2-2. Unit Test 실행
- [x] 테스트 실행: `uv run pytest tests/unit/test_storage.py -v`
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

### 2-2. Unit Test 실행
- [x] 테스트 실행: `uv run pytest tests/unit/test_storage.py -v`

**Expected**: ChromaStorage 관련 테스트 통과

**커밋 메시지**:
```
refactor(spec-017): integrate gemini embedding api with chromadb

- Replace local all-MiniLM-L6-v2 with Gemini text-embedding-004
- Add embedding_function to ChromaStorage initialization
- Require GEMINI_API_KEY environment variable
```

---

## Task 3: 의존성 제거

### 3-1. pyproject.toml 수정
- [x] `onnxruntime>=1.16.0` 제거
- [x] `tokenizers>=0.15.0` 제거

### 3-2. 의존성 업데이트
- [x] 실행: `uv lock`
- [x] 실행: `uv sync`

### 3-3. 의존성 검증
- [x] 실행: `uv tree | grep -E "(onnxruntime|tokenizers)"`

**Expected**: 출력 없음 (완전히 제거됨)

**커밋 메시지**:
```
chore(spec-017): remove heavy ml dependencies

- Remove onnxruntime (no longer needed)
- Remove tokenizers (no longer needed)
- ChromaDB now uses Gemini Embedding API
```

---

## Task 4: Integration Test 실행 및 수정

### 4-1. Docker 환경 준비 및 초기 문제 발견
- [x] 실행: `docker-compose up -d backend`
- [x] 초기 테스트 실행 → **Connection Refused** 발견
- [x] Backend 로그 확인 → 컨테이너 크래시 발견

### 4-2. Docker 빌드 문제 해결
**문제**: Backend 컨테이너가 시작 직후 크래시
- [x] 로그 분석: `FileNotFoundError: pygments/lexer.py` (hardlink 실패)
- [x] **해결 1**: `ENV UV_LINK_MODE=copy` 추가 (Dockerfile)
- [x] **해결 2**: `.dockerignore` 생성 (로컬 .venv가 Docker 빌드를 덮어쓰는 문제 방지)
- [x] **해결 3**: CMD를 원래 `uv run` 방식으로 복원
- [x] Docker 재빌드 및 재시작 → **uvicorn 정상 실행 확인**

### 4-3. 환경변수 문제 해결
**문제**: API 500 에러 - `ValueError: GEMINI_API_KEY environment variable is required`
- [x] 원인 분석: docker-compose.yml에 GEMINI_API_KEY 누락
- [x] **해결**: docker-compose.yml backend 환경변수에 `GEMINI_API_KEY=${GOOGLE_API_KEY}` 추가
- [x] Backend 재시작 → **정상 작동 확인**

### 4-4. Integration Test 재실행 및 성공
- [x] 테스트 실행: 
```bash
uv run pytest -v tests/integration/bdd/ \
  -k "test_successful_entity_graph_auto_construction or \
      test_entity_based_document_search or \
      test_entity_deduplication or \
      test_duplicate_url_sequential_ingestion"
```

**결과**: ✅ **4 passed in 61.00s**
- ✅ `test_successful_entity_graph_auto_construction` PASSED
- ✅ `test_entity_based_document_search` PASSED
- ✅ `test_entity_deduplication` PASSED
- ✅ `test_duplicate_url_sequential_ingestion` PASSED

### 4-5. 에디터 설정
- [x] `.vscode/settings.json` 생성 (Python 3.12 인터프리터 자동 선택)

**커밋**: `7a41644`
```
feat(spec-017): fix Docker build and add GEMINI_API_KEY support

- Added .dockerignore to prevent local .venv from overwriting Docker build
- Added ENV UV_LINK_MODE=copy to fix uv sync file system issues
- Reverted CMD to original 'uv run' approach (working solution)
- Added GEMINI_API_KEY environment variable to docker-compose.yml
- All 4 integration tests now passing ✅
```

---

## Task 5: 전체 테스트 스위트 실행

### 5-1. 전체 테스트 실행
- [x] 테스트 실행: `uv run pytest -v`
- [x] **결과**: 96 passed, 5 skipped, 24 warnings ✅
- [x] 이전 4개 FAILED → PASSED 확인
- [x] 기존 통과 테스트 → 여전히 PASSED (회귀 없음)

### 5-2. 추가 문제 발견 및 수정
- [x] Entity 엔드포인트 404 문제 발견 (entity 이름에 `/` 포함 시)
- [x] `entities.py`에 `:path` converter 적용
- [x] `test_knowledge_graph.py`에 URL 인코딩 추가
- [x] 모든 테스트 통과 확인

**커밋**: `c7bb00a`

---

## Task 6: Docker 환경 검증

### 6-1. Docker 재빌드 및 실행
- [x] 실행: `docker-compose down -v`
- [x] 실행: `docker-compose build`
- [x] 실행: `docker-compose up -d`

### 6-2. Health Check
- [x] 실행: `curl http://localhost:8000/docs`
- [x] **결과**: Swagger UI 정상 작동 (200 OK)

### 6-3. Integration Test 재실행
- [x] 테스트 실행: `uv run pytest -v tests/integration/bdd/`
- [x] **결과**: Docker 환경에서도 모든 테스트 통과 ✅

### 6-4. Docker 이미지 크기 비교
- [x] 실행: `docker images | grep rag-ingestion`
- [x] 현재 크기: **862MB** (ML 라이브러리 제거로 최적화됨)

---

## Task 7: 백로그 업데이트

### 7-1. backlog/queue.md 수정
- [x] Spec 017을 Phase 3에 추가 (상태: `[x]`)
- [x] Note에 수정된 테스트 목록 추가

**커밋 메시지**:
```
docs: mark spec 017 as completed in backlog
```

---

## Task 8: PR 준비 및 생성

### 8-1. walkthrough.md 작성
- [x] `walkthrough.md` 작성 완료
  - [x] 변경 사항 요약 (Gemini API 전환, Docker 수정)
  - [x] 테스트 결과 (96 passed)
  - [x] Docker 이미지 크기 (862MB)

### 8-2. pr_description.md 작성
- [x] `pr_description.md` 작성 완료
  - [x] 📋 Summary
  - [x] 🛠 Changes
  - [x] ✅ Verification

### 8-3. Push 및 PR 생성
- [x] Push: `git push origin feature/017-embedding-strategy-refactoring`
- [x] PR 생성: `gh pr create ...` (PR #19)

---

## Task 9: API Key Consolidation (Cleanup)

### 9-1. LLMFactory 테스트 작성 (TDD)
- [x] `tests/unit/test_llm_factory.py` 생성
- [x] `GEMINI_API_KEY` 우선순위 및 Backward Compatibility 테스트 (Strict Mode로 변경됨)

### 9-2. 코드 리팩토링
- [x] `app/core/llm.py`: `GEMINI_API_KEY` 지원 추가 및 `GOOGLE_API_KEY` 제거
- [x] `scripts/manual_verify_extraction.py`: `GEMINI_API_KEY` 지원 추가 및 `GOOGLE_API_KEY` 제거

### 9-3. 설정 파일 정리
- [x] `docker-compose.yml`: `GOOGLE_API_KEY` 의존성 제거
- [x] `.env` `GOOGLE_API_KEY` 삭제 확인

**Result**: 모든 환경에서 `GEMINI_API_KEY`로 단일화 완료.



```

---

## Summary

**총 Task**: 8개
1. ⏳ 브랜치 생성 및 현재 테스트 상태 확인 (2 subtasks)
2. ⏳ ChromaDB Embedding 설정 변경 (2 subtasks)
3. ⏳ 의존성 제거 (3 subtasks)
4. ⏳ Integration Test 실행 및 수정 (3 subtasks)
5. ⏳ 전체 테스트 스위트 실행 (2 subtasks)
6. ⏳ Docker 환경 검증 (4 subtasks)
7. ⏳ 백로그 업데이트
8. ⏳ PR 준비 및 생성 (3 subtasks)

**예상 커밋 수**: 4-6개

**핵심 리스크**:
- Gemini API Rate Limit
- Embedding 품질 변화
- Docker 환경 이슈
