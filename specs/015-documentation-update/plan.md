# Implementation Plan: Spec 015 - Documentation Update

## 📋 Branch Strategy

```bash
feature/015-documentation-update
```

**single commit per task** 원칙 준수

---

## 🎯 Core Strategy

### 1. 3-Phase Approach

**Phase 1: Analysis** (문서

 조사)
- 현재 docs, specs 디렉토리 문서 목록화
- 중복/이동 대상 문서 파악
- README 누락 항목 리스트업

**Phase 2: Restructuring** (구조 개선)
- specs → docs 문서 이동
- 중복 문서 병합
- docs 디렉토리 구조 정리

**Phase 3: Update** (내용 업데이트)
- README 최신화
- Cross-reference 정리
- 링크 검증

### 2. 문서 분류 기준

| 위치 | 용도 | 예시 |
|------|------|------|
| **docs/** | 재사용 가능한 참고 문서 | architecture.md, ontology.md, testing_strategy.md |
| **specs/** | Spec별 구현 기록 | spec.md, plan.md, task.md, walkthrough.md |
| **README.md** | 프로젝트 개요 및 현재 상태 | 전체 개요, Quick Start, 완료 Spec 상태 |

---

## 📂 Proposed Changes

### 1. docs 디렉토리 재구성

#### 이동 대상 문서

```bash
# 1. Cypher Patterns (신규)
specs/010-knowledge-graph-construction/cypher_patterns.md 
  → docs/cypher_patterns.md

# 2. Ontology (병합 검토)
# docs/ontology.md 이미 존재
# specs/007-ontology-design/ontology.md와 비교 후 최신화

# 3. Testing Strategy (병합 검토)
# docs/testing_strategy.md 이미 존재
# specs/009-testing-strategy/testing_philosophy.md와 비교 후 최신화
```

#### 최종 docs 디렉토리 구조

```
docs/
├── admin_guide.md           # [유지] 서비스 실행 가이드
├── architecture.md          # [유지] Clean Architecture 설계
├── async_guide.md           # [유지] 비동기 처리 가이드
├── cypher_patterns.md       # [신규] Neo4j Cypher 패턴 모음
├── getting_started.md       # [유지] 빠른 시작 가이드
├── ontology.md              # [업데이트] Entity/Relationship 정의
├── tech_stack.md            # [유지] 기술 스택 선정 배경
└── testing_strategy.md      # [업데이트] 테스트 전략 및 철학
```

---

### 2. README 업데이트

#### 변경 사항

**Section: 현재 구현 상태 (Current Status)**

```diff
### ✅ Phase 3: Progressive Intelligence (진행 중)
- **Spec 005**: ✅ **Semantic Extraction** - Gemini 2.0 Flash를 활용한 메타데이터 추출
- **Spec 006**: ✅ **Clean Architecture Refactoring** - Domain 격리 및 확장성 개선
-- **Spec 007-008**: 🚧 **Ontology & Knowledge Graph** (예정)
+- **Spec 007**: ✅ **Ontology Design** - Entity/Relationship 타입 정의
+
+### ✅ Phase 4: Knowledge Graph & Testing (완료)
+- **Spec 008**: ✅ **Docker Integration Bugfix** - Neo4j Storage 생성자 수정
+- **Spec 009**: ✅ **Testing Strategy** - TDD/BDD 통합 테스트 전략 수립
+- **Spec 010**: ✅ **Knowledge Graph Construction** - Entity 자동 추출 및 그래프 구축
+- **Spec 011**: ✅ **Infrastructure Refactoring** - Repository 파일명 표준화, 주석 한글화
+
+### ✅ Phase 5: Code Quality & Documentation (완료)
+- **Spec 012**: ✅ **Integration Test High Priority** - Critical BDD 시나리오 추가
+- **Spec 013**: ✅ **Fix Failed Tests** - 테스트 회귀 수정
+- **Spec 014**: ✅ **Code Quality Improvement** - Bug fix + GWT 표준화
+- **Spec 015**: ✅ **Documentation Update** - 문서 최신화 및 재구성 (현재)
```

**Section: 📚 Documentation**

```diff
## 📚 Documentation

+### Core Guides
- **[Architecture](docs/architecture.md)**: Clean Architecture 설계 원칙 및 패턴
- **[Tech Stack](docs/tech_stack.md)**: 기술 선정 이유 및 장단점
+- **[Ontology](docs/ontology.md)**: Entity/Relationship 타입 정의 및 설계
+- **[Cypher Patterns](docs/cypher_patterns.md)**: Neo4j Cypher 쿼리 패턴 모음
+
+### Operation & Development
- **[Async Guide](docs/async_guide.md)**: 비동기 처리 및 백그라운드 작업
- **[Admin Guide](docs/admin_guide.md)**: 서비스 실행 및 관리
+- **[Testing Strategy](docs/testing_strategy.md)**: TDD/BDD 테스트 전략 및 철학
+
+### Project Management
- **[Backlog](backlog/queue.md)**: 프로젝트 로드맵 및 우선순위
```

---

### 3. Cross-Reference 정리

#### README → docs 링크 검증

모든 링크가 실제 파일을 가리키는지 확인:
- `[Architecture](docs/architecture.md)` ✓
- `[Tech Stack](docs/tech_stack.md)` ✓
- `[Ontology](docs/ontology.md)` ✓ (업데이트 후)
- `[Cypher Patterns](docs/cypher_patterns.md)` ✓ (신규)
등...

#### docs 내부 Cross-Reference

예시: `docs/ontology.md`에서 관련 문서 링크
```markdown
## 참고 문서
- [Knowledge Graph Construction (Spec 010)](../specs/010-knowledge-graph-construction/spec.md)
- [Architecture Guide](./architecture.md)
- [Cypher Patterns](./cypher_patterns.md)
```

---

## 🧪 Verification Plan

### 1. 링크 검증

```bash
# Markdown 링크 체크 (수동)
# README의 모든 링크 클릭 확인
# docs 문서의 상호 링크 확인
```

### 2. 문서 일관성 확인

- [ ] 모든 완료 Spec이 README에 표시됨
- [ ] docs 디렉토리의 모든 파일이 README에서 언급됨
- [ ] specs 디렉토리에 기술 참고 문서가 남아있지 않음

### 3. 사용자 리뷰

- docs 개선사항 확인
- README 가독성 확인
- 누락된 문서가 없는지 확인

---

## 📦 Commits

1. `docs: move cypher_patterns from specs to docs`
2. `docs: update ontology.md with latest entity types`
3. `docs: update testing_strategy.md with TDD/BDD approach`
4. `docs: update README with latest Spec status (010-015)`
5. `docs: add cross-references in docs directory`
6. `docs: update backlog queue.md`

---

## 🚨 주의사항

1. **Spec 문서는 수정하지 않음**
   - specs/XXX 디렉토리의 문서는 역사 기록
   - 복사만 하고 원본은 유지

2. **문서 이동 시 원본 유지**
   - specs에서 docs로 복사할 때, Spec 디렉토리에 "moved" 표시 파일 추가
   - 예: `cypher_patterns.md` 삭제 후 → `cypher_patterns_moved_to_docs.txt` 생성

3. **링크 상대경로 주의**
   - docs 내부: `./filename.md`
   - docs → specs: `../specs/XXX/filename.md`
   - specs → docs: `../../docs/filename.md`

---

## ✅ Definition of Done

- [x] spec.md, plan.md, task.md 작성 완료
- [ ] specs → docs 문서 이동 완료
- [ ] README 최신화 완료
- [ ] Cross-reference 정리 완료
- [ ] 모든 링크 검증 완료
- [ ] backlog 업데이트 완료
- [ ] 사용자 리뷰 및 승인
