# Spec 011: Infrastructure Layer Refactoring

## 🎯 목표

Infrastructure Layer의 일관성과 가독성을 개선하여 Clean Architecture 원칙을 더 충실히 준수합니다.

---

## 🔍 현재 문제점

### 1. 파일명 불일치

**Domain Interfaces (일관됨):**
- `document_repository.py` ✅
- `graph_repository.py` ✅
- `job_repository.py` ✅

**Infrastructure Storage (불일치):**
- ❌ `neo4j.py` → `Neo4jStorage` (DocumentRepository 구현)
- ❌ `neo4j_graph.py` → `Neo4jGraphRepository` (GraphRepository 구현)
- ❌ `neo4j_job_repo.py` → `Neo4jJobRepository` (JobRepository 구현)

**문제:**
- Interface 이름과 파일명 불일치
- 검색 어려움 ("repository"로 검색 시 일부만 찾아짐)
- 명확성 부족 (neo4j.py가 무엇을 구현하는지 불분명)

### 2. 주석 언어 혼용

**발견된 사례 (38개):**
```python
# Flatten metadata to avoid nested map errors in Neo4j  ← 영어
# Neo4j only allows primitives and arrays of primitives  ← 영어
# Entity 관련 쿼리  ← 한글
# Convert HTML to Markdown  ← 영어
```

**문제:**
- 일관성 부족
- 가독성 저하
- 팀 협업 시 혼란

### 3. Clean Architecture 개선 가능 항목

**발견된 사항:**
- `composite.py`: 주석이 너무 간략함
- `dependencies.py`: 주석이 너무 간략함 (역할 설명 부족)
- Type hints 일부 누락 (chroma.py의 `list_documents`)

---

## 💡 제안된 솔루션

### 1. 파일명 표준화

```
변경 전                    변경 후
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
neo4j.py          →       neo4j_document_repository.py
neo4j_graph.py    →       neo4j_graph_repository.py
neo4j_job_repo.py →       neo4j_job_repository.py
```

**장점:**
- Interface와 파일명 1:1 매칭
- 검색 용이성 향상
- 명확한 역할 표시

### 2. 주석 한글 통일

**원칙:**
- 모든 주석을 한글로 통일
- 도메인 용어는 영어 유지 (Repository, Entity 등)
- 필요시 영어 병기 (괄호 안)

**예시:**
```python
# Before
# Save to Graph (Structure & Metadata)

# After  
# Graph DB에 저장 (구조 및 메타데이터)
```

### 3. Clean Architecture 개선

**추가 작업:**
- `composite.py`: Storage 역할 및 책임 명확화 주석 추가
- `dependencies.py`: DI 컨테이너 역할 설명 주석 추가
- Type hints 완성

---

## 📊 영향 범위

### 변경될 파일

**파일명 변경 (3개):**
- `app/infrastructure/storage/neo4j.py` → `neo4j_document_repository.py`
- `app/infrastructure/storage/neo4j_graph.py` → `neo4j_graph_repository.py`
- `app/infrastructure/storage/neo4j_job_repo.py` → `neo4j_job_repository.py`

**Import 수정 필요 (10개 이상):**
- `app/interfaces/api/dependencies.py`
- `app/infrastructure/storage/composite.py`
- `tests/unit/test_*.py`
- `tests/contracts/test_*.py`
- 기타 의존 파일

**주석 수정 (38개 파일):**
- `app/` 전체

---

## ⚠️ Breaking Changes

**없음** - 인터페이스 변경 없이 파일명 및 주석만 수정

---

## ✅ Acceptance Criteria

1. ✅ 모든 Repository 구현 파일명이 Interface 이름과 일치함
2. ✅ 모든 주석이 한글로 통일됨 (도메인 용어 제외)
3. ✅ 기존 테스트 모두 통과 (45 passed, 2 skipped)
4. ✅ pylint/ruff 경고 없음
5. ✅ Import 경로 모두 업데이트됨

---

## 🔮 Future Work

- Type hints 100% 커버리지 (추후 Spec)
- Docstring 표준화 (추후 Spec)

---

**작성일:** 2026-01-18  
**우선순위:** Medium (품질 개선)  
**예상 소요 시간:** 2-3시간
