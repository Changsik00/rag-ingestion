# Spec 015: Documentation Update & Reorganization

## 📋 개요

프로젝트 문서를 최신 상태로 업데이트하고, 재사용 가능한 문서를 적절한 위치로 이동하여 문서 구조를 개선합니다.

---

## 🎯 목표

### 1. README 최신화
- **현재 문제**:
  - Spec 010 (Knowledge Graph Construction) 완료 상태가 반영되지 않음
  - Spec 011 (Infrastructure Refactoring) 누락
  - Spec 014 (Code Quality) 누락
  - "예정" 상태의 Spec들이 outdated

- **목표**:
  - 완료된 Spec (010, 011, 014) 상태 업데이트
  - Phase 구분 재정리
  - 최신 아키텍처 반영

### 2. docs 디렉토리 재구성
- **현재 문제**:
  - specs 디렉토리에 재사용 가능한 기술 문서가 산재
  - docs와 specs의 역할 구분이 불명확

- **목표**:
  - specs: Spec별 구현 문서 (spec.md, plan.md, task.md, walkthrough.md 등)
  - docs: 재사용 가능한 참고 문서 (architecture, ontology, testing_strategy 등)
  - 적절한 문서 이동 및 cross-referencing

### 3. specs → docs 이동 대상
다음 문서들을 docs로 이동:
- `specs/009-testing-strategy/testing_philosophy.md` → `docs/testing_strategy.md` (이미 있음, 병합 검토)
- `specs/007-ontology-design/ontology.md` → `docs/ontology.md` (이미 있음, 최신화 검토)
- `specs/010-knowledge-graph-construction/cypher_patterns.md` → `docs/cypher_patterns.md` (신규)

### 4. 문서 일관성 검토
- 모든 docs 문서 간 링크 검증
- README에서 docs 문서로의 링크 정확성 확인
- 용어 통일 (한영 혼용 개선)

---

## 📐 범위

### In-Scope
✅ README 업데이트
✅ specs → docs 문서 이동
✅ docs 내부 cross-reference 정리
✅ 주요 링크 검증

### Out-of-Scope
❌ 개별 Spec 문서 내용 수정 (각 Spec는 역사 기록으로 유지)
❌ 코드 변경 (문서만)
❌ 새로운 기능 문서 작성

---

## 🔍 현재 주요 문제

### 1. README 불일치
```markdown
# 현재 README (라인 19-27)
### ✅ Phase 3: Progressive Intelligence (진행 중)
- **Spec 005**: ✅ **Semantic Extraction**
- **Spec 006**: ✅ **Clean Architecture Refactoring**
- **Spec 007-008**: 🚧 **Ontology & Knowledge Graph** (예정)
```

**문제**: Spec 007은 완료, Spec 010 (Knowledge Graph)도 완료됨. Spec 011, 014 누락.

### 2. docs vs specs 역할 혼재
- `docs/ontology.md`: 이미 존재하지만 Spec 007과 내용 중복 가능성
- `docs/testing_strategy.md`: Spec 009와 중복
- `specs/010-.../cypher_patterns.md`: docs로 이동 필요

---

## ✅ Success Criteria

1. ✅ README가 최신 완료 Spec (001-014) 반영
2. ✅ specs 디렉토리의 재사용 문서가 docs로 이동
3. ✅ docs 디렉토리 내 cross-reference 정리
4. ✅ 모든 링크 검증 (README → docs, docs → docs)
5. ✅ 문서 일관성 확보 (용어, 구조)

---

## 📚 참고

- 현재 README: [README.md](file:///Users/ck/Project/doit/rag-ingestion/README.md)
- 현재 docs: [docs/](file:///Users/ck/Project/doit/rag-ingestion/docs/)
- 현재 specs: [specs/](file:///Users/ck/Project/doit/rag-ingestion/specs/)
- Backlog: [backlog/queue.md](file:///Users/ck/Project/doit/rag-ingestion/backlog/queue.md)
