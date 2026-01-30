# Task List: Spec-050 (Clean Architecture Refactoring)

## Progress
- [x] Spec 번호 확정 및 브랜치 생성
- [x] spec.md 작성 (12개 문제 반영)
- [x] plan.md 작성 (Phase A/B/C 구성)
- [x] task.md 작성
- [x] Architecture Diagnosis 문서화
- [ ] 백로그 업데이트
- [x] User Plan Accept ✅

---

## ═══════════════════════════════════════  
## Phase A: 기반 수정 (Critical Path)
## ═══════════════════════════════════════

### Task A-1: Dependency Rule Enforcement

#### A-1-1. Application Layer 생성 ✅
- [x] 디렉토리 생성: `mkdir -p app/application/services`
- [x] `__init__.py` 생성
- [x] Commit: `chore(spec-050): create application services directory`

#### A-1-2. IntegrityService 이동 ✅
- [x] 파일 이동: `app/domain/services/storage_integrity_service.py` → `app/application/services/integrity_service.py`
- [x] 클래스명 변경: `StorageIntegrityService` → `IntegrityService`
- [ ] Import 수정: `Any` → `DocumentRepository`, `VectorRepository` Protocol (Phase B-3에서 처리)
- [x] Commit: `refactor(spec-050): move IntegrityService to application layer`

#### A-1-3. LLMFactory 이동 ✅
- [x] 디렉토리 생성: `mkdir -p app/infrastructure/factories`
- [x] 파일 이동: `app/core/llm.py` → `app/infrastructure/factories/llm_factory.py`
- [ ] 반환 타입 변경: `LangChainLLMAdapter` → `LLMInterface` (Phase B-3에서 처리)
- [x] `app/core/llm.py` 삭제
- [x] Commit: `refactor(spec-050): move LLMFactory to infrastructure layer`

#### A-1-4. Import 경로 업데이트 (Dependency Injection) ✅
- [x] `app/interfaces/api/dependencies.py` 수정
- [x] `app/application/admin/integrity_service.py` Import 수정
- [x] `tests/unit/` Import 수정
- [x] Commit: `refactor(spec-050): update DI imports for integrity and llm`

#### A-1-5. 검증 (Phase A-1) ✅
- [x] Test 실행: `uv run pytest tests/ -v` (126 passed, 20 failed)
- [x] Import 검증: Layer violation 제거 완료
- [x] 실패 테스트 분석: 나머지는 LLM async mocking 관련 (기존 이슈)
- [x] Commit: `fix(spec-050): update LLMFactory mocking paths in tests`

---

### Task A-2: Domain Object Reorganization

#### A-2-1. Domain Schemas → Value Objects 이동
- [ ] `app/domain/schemas/extraction.py` → `app/domain/value_objects/extracted_metadata.py`
- [ ] `app/domain/schemas/intent.py` → `app/domain/value_objects/intent.py`
- [ ] `app/domain/schemas/ontology.py` → `app/domain/value_objects/ontology.py`
- [ ] `app/domain/schemas/` 디렉토리 삭제
- [ ] Commit: `refactor(spec-050): reorganize domain schemas to value objects`

#### A-2-2. API Schemas 이동
- [ ] `app/schemas/` → `app/interfaces/api/schemas/` 이동
- [ ] `app/schemas/` 디렉토리 삭제
- [ ] Commit: `refactor(spec-050): move API schemas to interfaces layer`

#### A-2-3. DocumentMetadata VO 생성
- [ ] 파일 생성: `app/domain/value_objects/document_metadata.py`
- [ ] `Document.metadata: dict` → `metadata: DocumentMetadata` 변경
- [ ] Commit: `refactor(spec-050): create DocumentMetadata value object`

#### A-2-4. Import 경로 전면 업데이트
```bash
# 영향받는 모든 파일 검색 및 수정
grep -r "from app.domain.schemas" app/ tests/
grep -r "from app.schemas" app/ tests/
```
- [ ] 검색된 파일들의 Import 경로 수정
- [ ] Commit: `refactor(spec-050): update imports for reorganized schemas`

#### A-2-5. 검증 (Phase A-2)
- [ ] Test 실행: `uv run pytest tests/ -v`
- [ ] Linter: `uv run ruff check app/ tests/`

---

### Task A-3: Application Layer Consolidation

#### A-3-1. Use Cases → Application Services 통합
- [ ] `app/use_cases/ingestion.py` → `app/application/services/ingestion_service.py`
- [ ] 파일명 변경: `IngestionService` 유지 (이미 Service)
- [ ] `app/use_cases/` 디렉토리 삭제
- [ ] Commit: `refactor(spec-050): consolidate use_cases into application layer`

#### A-3-2. Import 경로 업데이트
```bash
grep -r "from app.use_cases" app/ tests/
```
- [ ] API dependencies 수정
- [ ] Admin 페이지 Import 수정
- [ ] Tests Import 수정
- [ ] Commit: `refactor(spec-050): update imports after use_cases removal`

#### A-3-3. 검증 (Phase A 완료)
- [ ] Test 실행: `uv run pytest tests/ -v`
- [ ] 디렉토리 확인: `ls app/use_cases/` → "No such file" 기대
- [ ] Admin UI 실행: 정상 작동 확인

---

## ═══════════════════════════════════════  
## Phase B: 품질 개선
## ═══════════════════════════════════════

### Task B-1: Naming Convention Standardization

#### B-1-1. Repository 클래스명 변경
- [ ] `Neo4jStorage` → `Neo4jDocumentRepository`
- [ ] `CompositeStorage` → `CompositeDocumentRepository`
- [ ] `ChromaStorage` → `ChromaVectorRepository`
- [ ] Commit: `refactor(spec-050): standardize repository naming`

#### B-1-2. Import 경로 업데이트
```bash
grep -r "Storage" app/ tests/
```
- [ ] 모든 `Storage` 참조를 `Repository`로 변경
- [ ] Commit: `refactor(spec-050): update imports after repository rename`

#### B-1-3. 검증 (Phase B-1)
- [ ] Test 실행: `uv run pytest tests/ -v`
- [ ] Storage 용어 검증: `grep -r "Storage" app/` → 0건 (파일명 제외)

---

### Task B-2: Service Layer Cohesion

#### B-2-1. Infrastructure Service 재배치
- [ ] `app/domain/services/chunker_service.py` → `app/infrastructure/chunker/chunker_service.py`
- [ ] `app/domain/services/file_processor.py` → `app/infrastructure/processors/file_processor.py`
- [ ] `app/domain/services/web_scraper_service.py` 삭제 (중복)
- [ ] Commit: `refactor(spec-050): relocate infrastructure services`

#### B-2-2. Import 경로 업데이트
```bash
grep -r "from app.domain.services.chunker_service" app/
grep -r "from app.domain.services.file_processor" app/
```
- [ ] 모든 Import 경로 수정
- [ ] Commit: `refactor(spec-050): update imports after service relocation`

#### B-2-3. Domain Services 정리 확인
- [ ] `app/domain/services/`에 남은 파일:
  - `intent_classifier.py` ✅
  - `query_rewriter.py` ✅
  - `semantic_extractor.py` ✅
  - `admin_agent.py` (Phase C에서 이동 예정)

#### B-2-4. 검증 (Phase B-2)
- [ ] Test 실행: `uv run pytest tests/ -v`

---

### Task B-3: Protocol Enforcement

#### B-3-1. VectorRepository Protocol 생성
- [ ] 파일 생성: `app/domain/interfaces/vector_repository.py`
```python
class VectorRepository(Protocol):
    def save_chunks(self, chunks: list) -> None: ...
    def get_all_chunk_ids(self) -> set[str]: ...
```
- [ ] Commit: `feat(spec-050): add VectorRepository protocol`

#### B-3-2. IntegrityService Any 타입 제거
- [ ] `primary_repo: Any` → `primary_repo: DocumentRepository`
- [ ] `target_repo: Any` → `target_repo: VectorRepository`
- [ ] Commit: `refactor(spec-050): replace Any with Protocols in IntegrityService`

#### B-3-3. 검증 (Phase B 완료)
- [ ] Test 실행: `uv run pytest tests/ -v`
- [ ] Type Check (Optional): `mypy app/application/services/integrity_service.py`

---

## ═══════════════════════════════════════  
## Phase C: 마무리
## ═══════════════════════════════════════

### Task C-1: Client-Agnostic Naming

#### C-1-1. AdminAgent → RAGAgent 이동 및 이름 변경
- [ ] 디렉토리 생성: `mkdir -p app/application/clients/admin`
- [ ] 파일 이동: `app/domain/services/admin_agent.py` → `app/application/clients/admin/rag_agent.py`
- [ ] 클래스명 변경: `AdminAgent` → `ConversationalRAGAgent`
- [ ] Commit: `refactor(spec-050): rename AdminAgent to ConversationalRAGAgent`

#### C-1-2. Import 경로 업데이트
```bash
grep -r "AdminAgent" app/ tests/
```
- [ ] 모든 Import 및 타입 힌트 수정
- [ ] Commit: `refactor(spec-050): update imports after agent rename`

---

### Task C-2: Shared Utilities Layer

#### C-2-1. Shared 디렉토리 생성
- [ ] 디렉토리 생성: `mkdir -p app/shared`
- [ ] `app/core/logging_config.py` → `app/shared/logging.py` 이동
- [ ] Commit: `refactor(spec-050): create shared utilities layer`

#### C-2-2. Import 경로 업데이트
```bash
grep -r "from app.core.logging_config" app/
```
- [ ] 모든 Import 경로 수정
- [ ] Commit: `refactor(spec-050): update logging imports`

#### C-2-3. Core 디렉토리 정리 확인
- [ ] `app/core/`에 남은 파일:
  - `config.py` ✅
  - `exceptions.py` ✅

---

### Task C-3: Documentation Update

#### C-3-1. Architecture 문서 업데이트
- [ ] `docs/architecture/architecture.md` 전면 재작성
  - Clean Architecture 4계층 명시
  - Hexagonal 용어 제거
  - 디렉토리 구조 다이어그램 업데이트
- [ ] Commit: `docs(spec-050): update architecture documentation`

#### C-3-2. ADR 작성
- [ ] 파일 생성: `docs/architecture_decisions/adr-001-clean-architecture-refactoring.md`
- [ ] 내용: 왜 리팩토링했는지, 어떤 트레이드오프가 있었는지 기록
- [ ] Commit: `docs(spec-050): add ADR for clean architecture refactoring`

#### C-3-3. 백로그 업데이트
- [ ] `backlog/queue.md`에 Spec 050 완료 상태 업데이트
- [ ] Commit: `docs(spec-050): update backlog status`

---

## ═══════════════════════════════════════  
## Final: PR Creation & Archiving
## ═══════════════════════════════════════

### Task Final-1: Manual Verification

#### Final-1-1. Admin UI 동작 확인
- [ ] Streamlit 실행: `uv run streamlit run app/admin/1_File_Ingestion.py`
- [ ] 모든 페이지 접근 테스트
- [ ] RAG Playground 정상 작동 확인

#### Final-1-2. API 엔드포인트 확인
- [ ] FastAPI 서버 실행: `uv run uvicorn app.interfaces.api.main:app --reload`
- [ ] Swagger UI: `http://localhost:8000/docs`
- [ ] 주요 엔드포인트 테스트 (Ingest, Jobs, Admin)

#### Final-1-3. Import 레이어 검증
```bash
# Domain이 Infrastructure를 참조하지 않는지 확인
grep -r "from app.infrastructure" app/domain/

# use_cases 디렉토리 삭제 확인
ls app/use_cases/
```
- [ ] 결과 확인: Domain → Infrastructure 참조 0건
- [ ] use_cases 디렉토리 없음

---

### Task Final-2: Code Quality & Tests

#### Final-2-1. Code Quality Check
- [ ] Linter: `uv run ruff check . --fix`
- [ ] Formatter: `uv run ruff format .`

#### Final-2-2. Full Test Suite
- [ ] 전체 Test: `uv run pytest tests/ -v`
- [ ] 결과 확인: **87+ passed, 0 failed**

---

### Task Final-3: PR Creation

#### Final-3-1. Walkthrough 작성
- [ ] **Walkthrough 작성**: `specs/050-dependency-rule-enforcement/walkthrough.md`
  - Phase별 변경 사항 요약
  - Before/After 디렉토리 구조 비교
  - 테스트 결과 스크린샷

#### Final-3-2. PR Description 작성
- [ ] **PR Description 작성**: `specs/050-dependency-rule-enforcement/pr_description.md`
  - 템플릿 준수: `docs/templates/pr_description.md`
  - 한국어 작성
  - 이모지 포함
  - 12개 문제 해결 내역 요약

#### Final-3-3. Archive Commit
- [ ] Archive Commit:
```bash
git add specs/050-dependency-rule-enforcement/walkthrough.md
git add specs/050-dependency-rule-enforcement/pr_description.md
git commit -m "docs(spec-050): archive walkthrough and pr description"
```

#### Final-3-4. Create PR
- [ ] PR 생성:
```bash
gh pr create \
  --title "refactor(spec-050): clean architecture refactoring" \
  --body-file specs/050-dependency-rule-enforcement/pr_description.md
```

---

## Summary

**총 Phase**: 3개 (A, B, C)  
**총 Task**: 15개  
**예상 커밋 수**: 13개  
**현재 진행**: Planning

**Phase별 예상 시간**:
- Phase A (기반 수정): 6시간
- Phase B (품질 개선): 5시간
- Phase C (마무리): 3시간
- **총 14시간**

**체크리스트**:
- [/] Planning (spec.md, plan.md, task.md 작성)
- [ ] Execution (Phase A → B → C 순차 실행)
- [ ] Verification (수동 검증 및 PR 생성)
