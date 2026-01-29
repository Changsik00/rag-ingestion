# Task List: Spec 015 - Documentation Update

## Progress

- [x] Spec 번호 확정 (015)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [x] 사용자 승인 대기
- [x] 브랜치 생성 및 구현 시작

---

## Task 1: 브랜치 생성 및 Spec 문서 커밋

- [x] 브랜치 생성: `git checkout -b feature/015-documentation-update`
- [x] 브랜치 확인: `git branch --show-current`
- [x] Spec 문서 커밋 (이미 main에서 커밋됨)

**커밋 메시지:**
```
docs: add spec 015 - documentation update

- Add documentation reorganization spec
- Update backlog with Spec 015
```

---

## Task 2: specs → docs 문서 이동

### 2-1. Neo4j 문서 이동

- [x] 파일 복사: `neo4j-query-guide.md` → `docs/neo4j_query_guide.md`
- [x] 파일 복사: `graph-schema-explained.md` → `docs/graph_schema.md`
- [x] 원본 위치에 moved 표시: `MOVED.txt` 생성
- [x] 커밋: `docs: move neo4j documentation from spec 010 to docs directory`

**커밋 메시지:**
```
docs: move neo4j documentation from spec 010 to docs directory

- Copy neo4j-query-guide.md to docs/neo4j_query_guide.md
- Copy graph-schema-explained.md to docs/graph_schema.md
- Add reference marker in original location
- Make Neo4j documentation reusable across projects
```

### 2-2. ontology.md 업데이트

- [x] `docs/ontology.md`와 `specs/007-ontology-design/ontology.md` 비교
- [x] 최신 내용으로 `docs/ontology.md` 업데이트 (Spec 007, 010 내용 반영)
- [x] 커밋: `docs: update ontology.md with knowledge graph references`

**커밋 메시지:**
```
docs: update ontology.md with latest entity types

- Update entity types based on Spec 007
- Add knowledge graph patterns from Spec 010
- Improve cross-references
```

### 2-3. testing_strategy.md 업데이트

- [x] `docs/testing_strategy.md`와 `specs/009-testing-strategy/testing_philosophy.md` 비교
- [x] TDD/BDD 내용으로 `docs/testing_strategy.md` 업데이트
- [x] 커밋: `docs: update testing_strategy.md with latest metadata`

**커밋 메시지:**
```
docs: update testing_strategy.md with TDD/BDD approach

- Incorporate testing philosophy from Spec 009
- Add TDD/BDD examples
- Update test structure guidelines
```

---

## Task 3: README 최신화

### 3-1. Phase 구분 재정리

- [x] Phase 3-5 추가
- [x] Spec 001-015 상태 업데이트
- [x] 완료/진행중 표시 정확화
- [x] 커밋: `docs: update readme with spec 010-015 status and phase 4-5`

**커밋 메시지:**
```
docs: update readme with spec 010-015 status and phase 4-5

- Add Phase 4: Knowledge Graph & Testing
- Add Phase 5: Code Quality & Documentation
- Update completion status for Spec 007-015
- Reorganize phase descriptions
```

### 3-2. Documentation 섹션 개선

- [x] docs 디렉토리 새 문서 추가 (ontology.md, graph_schema.md, neo4j_query_guide.md)
- [x] 문서를 카테고리별로 그룹화 (Core Guides, Operation, Project Management)
- [x] 모든 링크 검증
- [x] 커밋에 포함됨

**커밋 메시지:**
```
docs: improve Documentation section in README

- Add Ontology and Cypher Patterns links
- Categorize docs (Core Guides, Operation, Project Management)
- Verify all documentation links
```

---

## Task 4: Cross-Reference 정리

### 4-1. docs 내부 상호 참조 추가

- [x] `docs/ontology.md`에 관련 문서 링크 추가 (Task 2-2에서 완료)
- [x] `docs/graph_schema.md`, `docs/neo4j_query_guide.md` 추가 (Task 2-1에서 완료)
- [x] `docs/architecture.md` 업데이트 (필요 없음 - 이미 최신 상태)
- [x] 별도 커밋 (Task 2에서 이미 포함됨)

**커밋 메시지:**
```
docs: add cross-references in docs directory

- Link ontology.md to architecture.md and cypher_patterns.md
- Link cypher_patterns.md to relevant Spec 010
- Improve document discoverability
```

---

## Task 5: 검증 및 마무리

### 5-1. 링크 검증

- [x] README의 모든 docs 링크 클릭 확인
- [x] docs 문서들의 상호 링크 확인
- [x] 상대경로 정확성 검증

### 5-2. 문서 일관성 확인

- [x] 완료 Spec (001-015) 모두 README에 표시
- [x] docs 디렉토리의 모든 파일 README에서 언급
- [x] 용어 일관성 (한영 혼용 최소화)

### 5-3. Backlog 최종 업데이트

- [x] Spec 015 완료로 표시
- [x] 커밋: `docs: mark spec 015 as completed in backlog`

**커밋 메시지:**
```
docs: mark spec 015 as completed in backlog

- Update queue.md with completion status
- Spec 015 documentation update finished
```

---

## Task 6: PR 준비 및 생성

- [x] `specs/015-documentation-update/walkthrough.md` 작성
- [x] `specs/015-documentation-update/pr_description.md` 작성
- [x] Push: `git push origin feature/015-documentation-update`
- [x] PR 생성:
```bash
gh pr create --base main --head feature/015-documentation-update \
  --title "docs(spec-015): documentation update and reorganization" \
  --body-file specs/015-documentation-update/pr_description.md
```

---

## Summary

**총 Task**: 6개
1. ✅ 브랜치 생성 및 Spec 문서 커밋
2. ⏳ specs → docs 문서 이동 (3 subtasks)
3. ⏳ README 최신화 (2 subtasks)
4. ⏳ Cross-Reference 정리
5. ⏳ 검증 및 마무리 (3 subtasks)
6. ⏳ PR 준비 및 생성

**예상 커밋 수**: 7-8개
