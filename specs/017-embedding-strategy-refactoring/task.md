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
- [/] Task 3 진행 중: 의존성 제거

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
- [/] 테스트 실행: `uv run pytest tests/unit/test_storage.py -v`
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
- [ ] 테스트 실행: `uv run pytest tests/unit/test_storage.py -v`

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
- [ ] `onnxruntime>=1.16.0` 제거
- [ ] `tokenizers>=0.15.0` 제거

### 3-2. 의존성 업데이트
- [ ] 실행: `uv lock`
- [ ] 실행: `uv sync`

### 3-3. 의존성 검증
- [ ] 실행: `uv tree | grep -E "(onnxruntime|tokenizers)"`

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

### 4-1. Docker 환경 준비
- [ ] 실행: `docker-compose down -v`
- [ ] 실행: `docker-compose up -d`
- [ ] 환경변수 확인: `.env` 파일에 `GEMINI_API_KEY` 존재 확인

### 4-2. 4개 실패 테스트 재실행
- [ ] 테스트 실행: `uv run pytest -v tests/integration/bdd/ -k "test_successful_entity_graph_auto_construction or test_entity_based_document_search or test_entity_deduplication or test_duplicate_url_sequential_ingestion"`

**시나리오**:
1. **성공**: 모든 테스트 통과 → Task 5로 진행
2. **실패**: 에러 분석 및 디버깅

### 4-3. 디버깅 (필요 시)
- [ ] 에러 로그 분석
- [ ] 코드 수정 또는 환경설정 조정
- [ ] 로깅 추가
- [ ] 테스트 재실행

**커밋 메시지** (필요 시):
```
fix(spec-017): resolve gemini embedding integration issues

- Add proper error handling for API calls
- Improve logging for embedding process
```

---

## Task 5: 전체 테스트 스위트 실행

### 5-1. 전체 테스트 실행
- [ ] 테스트 실행: `uv run pytest -v`

**Expected**:
- 이전 4개 FAILED → PASSED
- 기존 통과 테스트 → 여전히 PASSED (회귀 없음)

### 5-2. 회귀 발생 시 수정
- [ ] 회귀 테스트 분석
- [ ] 코드 수정
- [ ] 테스트 재실행

---

## Task 6: Docker 환경 검증

### 6-1. Docker 재빌드 및 실행
- [ ] 실행: `docker-compose down -v`
- [ ] 실행: `docker-compose build`
- [ ] 실행: `docker-compose up -d`

### 6-2. Health Check
- [ ] 실행: `curl http://localhost:8000/docs`

**Expected**: Swagger UI 정상 작동

### 6-3. Integration Test 재실행
- [ ] 테스트 실행: `uv run pytest -v tests/integration/bdd/`

**Expected**: Docker 환경에서도 모든 테스트 통과

### 6-4. Docker 이미지 크기 비교
- [ ] 실행: `docker images | grep rag-ingestion`
- [ ] 이전 이미지 크기와 비교 기록

---

## Task 7: 백로그 업데이트

### 7-1. backlog/queue.md 수정
- [ ] Spec 017을 Phase 3에 추가
- [ ] 상태를 `[x]` (완료)로 표시
- [ ] Note에 수정된 테스트 목록 추가

**커밋 메시지**:
```
docs: mark spec 017 as completed in backlog

- Embedding strategy refactored to Gemini API
- 4 failing integration tests now pass
- Heavy ML dependencies removed
```

---

## Task 8: PR 준비 및 생성

### 8-1. walkthrough.md 작성
- [ ] `specs/017-embedding-strategy-refactoring/walkthrough.md` 작성
  - [ ] 변경 사항 요약
  - [ ] 테스트 결과
  - [ ] Docker 이미지 크기 비교

### 8-2. pr_description.md 작성
- [ ] `specs/017-embedding-strategy-refactoring/pr_description.md` 작성
  - [ ] 📋 Summary
  - [ ] 🎯 Key Review Points
  - [ ] 🧪 Verification
  - [ ] 📦 Files Changed
  - [ ] 🚨 Breaking Changes
  - [ ] 📚 Related
  - [ ] ✅ Definition of Done

### 8-3. Push 및 PR 생성
- [ ] Push: `git push origin feature/017-embedding-strategy-refactoring`
- [ ] PR 생성:
```bash
gh pr create --base main --head feature/017-embedding-strategy-refactoring \
  --title "refactor(spec-017): embedding strategy refactoring" \
  --body-file specs/017-embedding-strategy-refactoring/pr_description.md
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
