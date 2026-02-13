# Implementation Plan: Spec-077

## 📋 Branch Strategy
- `feature/spec-077-phase8-documentation`

## 🛑 User Review Required
> [!NOTE]
> - 이 작업은 코드 변경 없이 **문서(Documentation)** 만 변경합니다.
> - `constitution.md`와 `agent.md`의 변경 사항은 향후 에이전트의 행동 지침이 되므로 주의 깊게 검토해 주십시오.

## 🎯 Core Strategy

### Architecture Context
이 작업은 시스템 아키텍처 변경이 아닌, 프로젝트 관리 및 프로세스 문서의 정비 작업입니다. 기존 Phase 8의 성과를 아카이브하고, 새로운 표준을 수립하는 것이 핵심입니다.

| Component | Strategy | Reasoning |
|:---:|:---|:---|
| **Archive** | New File (`docs/archive/`) | 기존 `queue.md`의 비대화를 막고 히스토리를 보존하기 위함 |
| **Backlog** | Cleanup | 현재 집중해야 할 Phase 9 및 이후 작업에 대한 가시성 확보 |
| **Standards** | `constitution.md` | Prompt Quality는 타협할 수 없는 품질 기준이므로 최상위 문서에 명시 |

## 📂 Proposed Changes

### Documentation (Archive)
#### [NEW] `docs/archive/phase_8_architecture_foundation.md`
- Markdown header: `# Phase 8: Architecture & Quality Foundation`
- Content: `backlog/queue.md`의 Phase 8 섹션 전체 복사 및 이동

### Documentation (Backlog)
#### [MODIFY] `backlog/queue.md`
- Phase 8 섹션 삭제
- 섹션 링크를 `docs/archive/phase_8_architecture_foundation.md`로 대체

### Documentation (Core)
#### [MODIFY] `.agent/constitution.md`
- **Section Addition**: `## 12. Prompt Engineering Standards`
    - Test Coverage Rule (20+ cases)
    - Versioning Rule
    - No Hard-coding Rule

#### [MODIFY] `.agent/agent.md`
- **Section Update**: Research Spec 처리 절차 추가
    - Definition of Done for Research
    - Trade-off Analysis Requirement

#### [MODIFY] `README.md`
- **Vision Redefinition**: "Knowledge Factory" 컨셉 강조 (Raw Data -> Wisdom)
- **Architecture Visualization**: 3-Layer Strategy (Atomic, Semantic, Knowledge) 다이어그램 추가
- **Content Restructuring**: 설치 가이드 분리, "Exploration" 용어 정제 ("Deep Structuring")

#### [NEW] `docs/guides/getting_started.md`
- 기존 `README.md`의 설치, 배포, 실행 방법 섹션 이동

## 🧪 Verification Plan

### Automated Tests
*N/A (문서 작업이므로 자동화 테스트 없음)*

### Manual Verification
1. **Link Check**:
    - `backlog/queue.md` -> `docs/archive/phase_8_architecture_foundation.md` 이동 클릭 테스트.
2. **Markdown Rendering**:
    - VSCode Preview를 통해 테이블, 인용구, 리스트 렌더링 확인.
3. **Content Verification**:
    - 아카이브된 내용이 누락 없이 원본과 동일한지 확인 (`diff` 또는 육안 검사).
