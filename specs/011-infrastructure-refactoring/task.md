# Task Checklist: Spec 011 - Infrastructure Refactoring

## Progress

- [x] Spec 번호 확정 (011)
- [x] spec.md 작성
- [x] plan.md 작성
- [x] task.md 작성
- [x] 사용자 승인 완료
- [x] 브랜치 생성 및 구현

---

## Task 1: 브랜치 생성 및 준비

- [x] 브랜치 생성: `git checkout -b feature/011-infrastructure-refactoring`
- [x] spec.md, plan.md, task.md 커밋
- [x] 커밋: `docs: add spec 011 - infrastructure refactoring`

---

## Task 2: 파일명 변경 (Phase 1)

- [x] `neo4j.py` → `neo4j_document_repository.py`
- [x] `neo4j_graph.py` → `neo4j_graph_repository.py`
- [x] `neo4j_job_repo.py` → `neo4j_job_repository.py`
- [x] 커밋: `refactor: standardize repository file naming`

---

## Task 3: Import 경로 업데이트 (Phase 2)

- [x] `dependencies.py` import 수정
- [x] `composite.py` import 수정
- [x] Tests import 수정
- [x] 커밋: `refactor: update import paths after file renaming`

---

## Task 4: 주석 한글화 - Storage Layer (Phase 3-1)

- [x] `neo4j_document_repository.py` 주석 한글화
- [x] `neo4j_graph_repository.py` 주석 한글화
- [x] `neo4j_job_repository.py` 주석 한글화
- [x] `chroma.py` 주석 한글화
- [x] `composite.py` 주석 한글화
- [x] 커밋: `docs: translate storage layer comments to Korean`

---

## Task 5: 주석 한글화 - 기타 (Phase 3-2)

- [x] `dependencies.py` 주석 한글화 및 상세화
- [x] `cypher_queries.py` 주석 한글화 (이미 한글)
- [x] `basic.py` 주석 한글화
- [x] Entities, Value Objects 주석 한글화 (대부분 영어 또는 주석 없음)
- [x] 커밋: `docs: translate all comments to Korean`

---

## Task 6: Clean Architecture 개선 (Phase 4)

- [x] Type hints 완성 (`chroma.py`)
- [x] Docstring 추가 (`composite.py`)
- [x] 주석 상세화 (`dependencies.py`)
- [ ] 커밋: `refactor: improve type hints and docstrings`

---

## Task 7: 테스트 실행 및 검증

- [ ] Contract Tests: `uv run pytest tests/contracts/ -v`
- [ ] Unit Tests: `uv run pytest tests/unit/ -v`
- [ ] Integration Tests: `docker compose up -d && uv run pytest tests/integration/ -v -m integration`
- [ ] Linter: `ruff check app/`
- [ ] Import 검증 스크립트 실행
- [ ] 모든 테스트 통과 확인

---

## Task 8: PR 준비 및 문서화

- [ ] `pr_description.md` 작성
- [ ] 모든 변경사항 커밋
- [ ] 푸시: `git push origin feature/011-infrastructure-refactoring`
- [ ] PR 생성: `gh pr create --title "refactor(spec-011): infrastructure layer refactoring" --body-file specs/011-infrastructure-refactoring/pr_description.md`

---

## Notes

- 파일명 변경은 `git mv` 사용 (Git history 유지)
- Import 업데이트는 자동화 불가, 수동 확인 필요
- 주석은 도메인 용어(Repository, Entity)는 영어 유지
- 기능 변경 없음, 리팩토링만 수행
