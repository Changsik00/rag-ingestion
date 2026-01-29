# Task Checklist: Clean Architecture Refactoring

## 0. 브랜치 생성
- [x] `main`에서 최신 코드 pull
- [x] `refactor/clean-architecture` 브랜치 생성
- [x] Spec 문서 작성 (`specs/refactor-clean-architecture/`)

---

## 1. Domain Layer - LLM Interface 추상화

### 1.1 Interface 정의
- [x] **`app/domain/interfaces/llm.py` 생성**
  - [x] `LLMInterface` Protocol 정의
  - [x] `extract_metadata()` 메서드 시그니처 정의
  - [x] 커밋: `feat(domain): add LLM interface abstraction`

---

## 2. Infrastructure Layer - LangChain Adapter

### 2.1 Adapter 구현
- [x] **`app/infrastructure/llm/__init__.py` 생성**
  - [x] 디렉토리 초기화
  
- [x] **`app/infrastructure/llm/langchain_adapter.py` 생성**
  - [x] 기존 `SemanticExtractor`의 LangChain 로직 이동
  - [x] `LangChainLLMAdapter` 클래스 구현
  - [x] `extract_metadata()` 메서드 구현
  - [x] 커밋: `feat(infra): implement LangChain adapter for LLM interface`

---

## 3. Domain Layer - SemanticExtractor 단순화

### 3.1 Service 리팩토링
- [x] **`app/domain/services/semantic_extractor.py` 수정**
  - [x] LangChain import 제거
  - [x] Core 레이어 import 제거
  - [x] `LLMInterface` Protocol 의존으로 변경
  - [x] 생성자 시그니처 변경: `__init__(self, llm: LLMInterface)`
  - [x] `extract()` 메서드를 `llm.extract_metadata()` 위임으로 단순화
  - [x] 커밋: `refactor(domain): simplify SemanticExtractor to use LLM interface`

---

## 4. Core & DI - Factory 및 의존성 주입 업데이트

### 4.1 LLM Factory 확장
- [x] **`app/core/llm.py` 수정**
  - [x] `LangChainLLMAdapter` import 추가
  - [x] `get_llm_adapter()` 메서드 추가
  - [x] `get_llm()` 함수가 Adapter를 반환하도록 수정
  - [x] 커밋: `refactor(core): update LLM factory to return adapter`

### 4.2 DI 설정 확인
- [x] **`app/interfaces/api/dependencies.py` 검토**
  - [x] `get_semantic_extractor()`가 Adapter를 주입하는지 확인
  - [x] 필요 시 수정 (일반적으로 변경 불필요)

---

## 5. 테스트 - 단위 테스트 업데이트

### 5.1 테스트 코드 리팩토링
- [x] **`tests/unit/domain/test_extractor.py` 수정**
  - [x] `LLMInterface` import 추가
  - [x] Mock을 Protocol 기반으로 변경
  - [x] `mock_llm.extract_metadata()` 사용하도록 수정
  - [x] 기존 LangChain Mock 코드 제거
  - [x] 커밋: `test: update extractor tests to use LLM interface`

---

## 6. 검증 - 테스트 실행

### 6.1 단위 테스트
- [x] **`uv run pytest tests/unit/domain/test_extractor.py -v` 실행**
  - [x] 모든 테스트 통과 확인
  
### 6.2 전체 단위 테스트
- [x] **`uv run pytest tests/unit/ -v` 실행**
  - [x] 기존 테스트 영향 없음 확인

### 6.3 통합 테스트
- [x] **`uv run python scripts/manual_verify_extraction.py` 실행**
  - [x] Gemini API 호출 정상 동작 확인
  - [x] 메타데이터 추출 품질 확인

### 6.4 전체 테스트
- [x] **`uv run pytest` 실행**
  - [x] 전체 테스트 통과 확인

---

## 7. 문서화

### 7.1 Walkthrough 작성
- [x] **리팩토링 요약 문서 작성**
  - [x] 변경 사항 요약
  - [x] Before/After 아키텍처 비교
  - [x] 테스트 결과 기록

---

## 8. PR 생성

### 8.1 PR 준비
- [x] **`specs/refactor-clean-architecture/pr_description.md` 작성**
  - [x] Summary 섹션
  - [x] Key Review Points 섹션
  - [x] Verification Plan 섹션
  - [x] 커밋: `docs: add PR description for clean architecture refactoring`

### 8.2 Push & PR
- [x] **`git push -u origin refactor/clean-architecture`**
- [x] **`gh pr create --body-file specs/refactor-clean-architecture/pr_description.md`**
