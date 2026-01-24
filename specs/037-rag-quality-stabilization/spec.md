# Spec-037: RAG Quality Stabilization & Storage Integrity

## 📋 배경 및 문제 정의 (Background & Problem)

### 1. 현상: 데이터 누락 및 불일치 (Distributed Drift)
- **현상**: Neo4j(1401개)와 ChromaDB(93개)의 데이터 개수가 일치하지 않음.
- **원인**: 인제스션 과정의 비원자적 연산으로 인한 '부분 성공' 발생.
- **결과**: 특정 문서의 일부 내용만 검색되거나 아예 검색되지 않는 현상 발생.

### 2. 현상: 문서 계층 관리 부실 (Document Integrity Issue)
- **현상**: 상위 문서(`Document`)의 제목이 하위 조각(`Chunk`)들에 제대로 전파되지 않거나, 제목 자체가 없는 문서가 존재함.
- **결과**: 검색 결과의 출처(Citation) 정보가 불분명해짐.

## 🔄 동기화 전략 (Sync Strategy)

### 1. Source of Truth (기준 데이터)
- **Neo4j(Graph DB)**를 '진실의 원천'으로 설정합니다.
- **Document-Chunk 계층 구조 활용**: `Document` 노드의 정보와 `Chunk` 노드의 정보를 상호 보완하여 동기화합니다.

### 2. 동기화 및 보정 원칙
- **Document-First Restoration**: `Document` 노드의 제목(Title)이 없는 경우 `Title Fallback` 로직으로 문서를 먼저 보정합니다.
- **Title Propagation**: 보정된 `Document` 제목을 모든 자식 `Chunk` 노드들에 강제로 전파(Sync)하여 데이터 규칙성을 확보합니다.
- **Differential Sync**: 문서 단위로 인덱싱 상태를 분석하여 '미수집(Missing)' 또는 '부분 수집(Partial)' 문서를 식별합니다.

## 🎯 요구사항 (Requirements)

### 1. [Admin] Document-Level Drift Monitor (문서 단위 관리)
- **Document Drift Table**: 단순히 청크 목록이 아닌 **"문서 리스트"** 단위로 정합성 표시.
  - **표시 항목**: 문서 제목, URL, 총 청크 수, ChromaDB에 저장된 청크 수, 인덱싱 상태(100%, Partial, 0%).
  - **상세 보기**: 특정 문서를 클릭하면 소속된 청크들의 미스매치 상세 내역(Content Snippet) 확인 가능.

### 2. [Admin] Selective Recovery (정밀 복구)
- **Fix by Document**: 특정 한 두 개의 문서만 골라서 재인덱싱하거나 메타데이터를 보정하는 기능.

### 3. [Core] Storage Integrity Service (고도화)
- `Document`와 `Chunk` 간의 유실된 관계를 탐지하고 복구하는 로직 추가.
- `Document` 제목을 자식 `Chunk`들에게 일괄 복사하는 기능.

## ✅ Definition of Done
1. Admin UI에서 "어떤 문서가 몇 % 인덱싱되었는지" 문서 단위로 확인 가능.
2. 제목이 없는 문서와 그 하위 청크들의 제목이 일관되게 보정됨.
3. "Sync Document" 기능을 통해 특정 문서의 누락된 청크만 선별 복구 완료.
