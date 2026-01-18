# Task List: Spec 015 - Documentation Update

## Progress

- [x] Spec 번호 확정 (015)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 백로그 업데이트
- [ ] 사용자 승인 대기
- [ ] 브랜치 생성 및 구현 시작

---

## Task 1: 브랜치 생성 및 Spec 문서 커밋

- [ ] 브랜치 생성: `git checkout -b feature/015-documentation-update`
- [ ] 브랜치 확인: `git branch --show-current`
- [ ] Spec 문서 커밋: `git add specs/015-documentation-update/ backlog/queue.md && git commit -m "docs: add spec 015 - documentation update"`

**커밋 메시지:**
```
docs: add spec 015 - documentation update

- Add documentation reorganization spec
- Update backlog with Spec 015
```

---

## Task 2: specs → docs 문서 이동

### 2-1. cypher_patterns.md 이동

- [ ] 파일 복사: `specs/010-knowledge-graph-construction/cypher_patterns.md` → `docs/cypher_patterns.md`
- [ ] 상대경로 링크 수정 (있으면)
- [ ] 원본 위치에 moved 표시: `specs/010-knowledge-graph-construction/cypher_patterns_moved.txt` 생성
- [ ] 커밋: `docs: move cypher_patterns to docs directory`

**커밋 메시지:**
```
docs: move cypher_patterns to docs directory

- Copy cypher_patterns.md from Spec 010 to docs/
- Add reference marker in original location
- Make it reusable across projects
```

### 2-2. ontology.md 업데이트

- [ ] `docs/ontology.md`와 `specs/007-ontology-design/ontology.md` 비교
- [ ] 최신 내용으로 `docs/ontology.md` 업데이트 (Spec 007, 010 내용 반영)
- [ ] 커밋: `docs: update ontology.md with latest entity types`

**커밋 메시지:**
```
docs: update ontology.md with latest entity types

- Update entity types based on Spec 007
- Add knowledge graph patterns from Spec 010
- Improve cross-references
```

### 2-3. testing_strategy.md 업데이트

- [ ] `docs/testing_strategy.md`와 `specs/009-testing-strategy/testing_philosophy.md` 비교
- [ ] TDD/BDD 내용으로 `docs/testing_strategy.md` 업데이트
- [ ] 커밋: `docs: update testing_strategy.md with TDD/BDD approach`

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

- [ ] Phase 3-5 추가
- [ ] Spec 001-015 상태 업데이트
- [ ] 완료/진행중 표시 정확화
-[ ] 커밋: `docs: update README with latest Spec status (010-015)`

**커밋 메시지:**
```
docs: update README with latest Spec status (010-015)

- Add Phase 4: Knowledge Graph & Testing
- Add Phase 5: Code Quality & Documentation
- Update completion status for Spec 007-015
- Reorganize phase descriptions
```

### 3-2. Documentation 섹션 개선

- [ ] docs 디렉토리 새 문서 추가 (cypher_patterns.md)
- [ ] 문서를 카테고리별로 그룹화 (Core Guides, Operation, Project Management)
- [ ] 모든 링크 검증
- [ ] 커밋: `docs: improve Documentation section in README`

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

- [ ] `docs/ontology.md`에 관련 문서 링크 추가
- [ ] `docs/cypher_patterns.md`에 관련 문서 링크 추가
- [ ] `docs/architecture.md` 업데이트 (필요시)
- [ ] 커밋: `docs: add cross-references in docs directory`

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

- [ ] README의 모든 docs 링크 클릭 확인
- [ ] docs 문서들의 상호 링크 확인
- [ ] 상대경로 정확성 검증

### 5-2. 문서 일관성 확인

- [ ] 완료 Spec (001-015) 모두 README에 표시
- [ ] docs 디렉토리의 모든 파일 README에서 언급
- [ ] 용어 일관성 (한영 혼용 최소화)

### 5-3. Backlog 최종 업데이트

- [ ] Spec 015 완료로 표시 (작업 완료 시)
- [ ] 커밋: `docs: mark spec 015 as completed in backlog`

**커밋 메시지:**
```
docs: mark spec 015 as completed in backlog

- Update queue.md with completion status
- Spec 015 documentation update finished
```

---

## Task 6: PR 준비 및 생성

- [ ] `specs/015-documentation-update/walkthrough.md` 작성
- [ ] `specs/015-documentation-update/pr_description.md` 작성
- [ ] Push: `git push origin feature/015-documentation-update`
- [ ] PR 생성:
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
