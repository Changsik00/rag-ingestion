# docs(spec-077): phase 8 documentation, archive, and readme renewal

## 📋 Summary

### 배경 및 목적
Phase 8 (Architecture & Quality Foundation) 작업 완료에 따른 문서화 및 백로그 정리를 진행합니다. 또한, 프로젝트의 비전과 아키텍처를 명확히 전달하기 위해 `README.md`를 **"Knowledge Factory"** 컨셉으로 전면 개편합니다.

### 주요 변경 사항
- [x] **Archive**: `backlog/archive.md`에 Phase 8(Spec 068~077) 완료 내역 추가.
- [x] **Backlog**: `backlog/queue.md` 정리 및 Phase 9 계획 수립.
- [x] **Core Docs**:
    - `constitution.md`: Prompt Quality Standard 추가.
    - `agent.md`: Research Spec 프로세스 명시.
- [x] **README Renewal (Knowledge Factory)**:
    - **Vision**: Raw Data -> Deep Structuring -> Knowledge Graph로 이어지는 흐름 강조.
    - **Architecture**: 3-Layer Storage Strategy (Atomic, Semantic, Knowledge) 시각화.
    - **Guide Separation**: 설치 및 배포 가이드를 `docs/guides/getting_started.md`로 분리.

## 🎯 Key Review Points
1. **README Clarity**: 새로운 `README.md`가 프로젝트의 가치를 잘 전달하는지, "Exploration" 대신 사용된 "Deep Structuring" 용어가 적절한지 확인 부탁드립니다.
2. **Archive Integrity**: Phase 8 완료 내역이 누락 없이 아카이빙되었는지 확인 바랍니다.

## 🧪 Verification

### Manual Verification
1. **README Rendering**: 메인 페이지의 다이어그램과 배지가 정상적으로 렌더링되는지 확인.
2. **Link Check**: `README.md` -> `docs/guides/getting_started.md` 링크 동작 확인.
3. **Archive 확인**: `backlog/archive.md` 포맷 일치 여부 확인.

## 📦 Files Changed

### 🆕 New Files
- `docs/guides/getting_started.md`: 설치 및 배포 가이드.
- `docs/archive/phase_8_architecture_foundation.md`: Phase 8 상세 아카이브.

### 🛠 Modified Files
- `README.md`: 전면 개편 (Vision & Architecture 중심).
- `backlog/archive.md`: Phase 8 요약 추가.
- `backlog/queue.md`: Phase 8 제거 및 Phase 9 추가.
- `.agent/constitution.md`: Quality Standard 추가.
- `.agent/agent.md`: Research Spec 추가.

## ✅ Definition of Done
- [x] `README.md` 전면 개편 및 가이드 분리 완료
- [x] Phase 8 아카이빙 완료
- [x] Core Docs (Constitution, Agent) 업데이트 완료
- [x] PR Description 업데이트 완료
