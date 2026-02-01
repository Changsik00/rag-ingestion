# Spec 052: Clean Architecture 계층 정제

## 🎯 목표
Spec 051 리팩토링 이후 남아있는 계층 경계 위반을 수정하고, 네이밍 일관성을 개선하며, 불필요한 파일 구조를 제거하여 Clean Architecture 원칙을 엄격히 적용합니다.

## 📋 배경

Spec 051의 대규모 리팩토링 이후에도 몇 가지 아키텍처 불일치가 남아있습니다:

1. **계층 위반**: 일부 인터페이스가 `application/`에 있어야 하는데 `domain/`에 위치
2. **네이밍 비일관성**: 파일명이 내용이나 동료 파일과 일치하지 않음
3. **불필요한 구조**: 일부 파일이 불필요한 중첩 사용 (예: `core/utils/`)
4. **중복 파일**: 레거시 파일이 리팩토링된 버전과 공존

## 🔍 해결할 이슈

### 1. 계층 경계 위반

**Domain → Application 이동:**
- `app/domain/interfaces/llm.py` → `app/application/interfaces/llm.py`
  - 이유: LLM은 인프라 관심사이며 핵심 도메인 개념이 아님
- `app/domain/interfaces/scraper.py` → `app/application/interfaces/scraper.py`
  - 이유: 웹 스크래핑은 외부 서비스이며 도메인 로직이 아님
- `app/domain/services/feedback.py` → `app/application/services/feedback.py`
  - 이유: LangGraph 워크플로우를 조율하는 Application 레벨 조정

### 2. Value Object 재정리

- `app/domain/models/document_metadata.py` → `app/domain/value_objects/document_metadata.py`
  - 이유: `DocumentMetadata`는 불변이며 식별자가 없음 (전형적인 VO)

### 3. 네이밍 일관성

**파일 이름 변경:**
- `app/application/services/admin_agent.py` → `app/application/services/agent.py`
  - `ConversationalRAGAgent`를 포함하며 "admin" 특화가 아님
- `app/application/services/ingestion.py` (IngestionUseCase) → 파일명 유지, 클래스명을 `Ingestion`으로 변경
  - `Integrity`, `Feedback`와 일관성 유지
- `app/core/utils/file_processor.py` → `app/core/file_processor.py`
  - `core/` 자체가 이미 유틸리티 성격을 내포
- `app/core/logging_config.py` → `app/core/logger.py`
  - 더 단순하고 관례적

### 4. State 객체 명확화

**현재 상태:**
- `app/domain/ingestion/state.py`에 `IngestionGraphState` 포함
- `app/domain/rag/state.py`에 `RAGGraphState` 포함

**검토 필요:**
이들은 기술적 제약이 있는 TypedDict 기반 LangGraph 상태입니다. 옵션:
1. domain에 유지하되 파일명 변경: `graph_state.py`
2. `infrastructure/ai/graphs/`로 이동 (사용처에 가까이)
3. `application/graph_states/` 생성 (중간 방안)

**권장안:** Domain에 유지하되 명확성을 위해 파일명 변경.

### 5. 중복 파일 정리

- 검증 및 제거: `app/interfaces/api/endpoints/jobs.py`가 `v1/endpoints/jobs.py`와 중복되는지 확인

## ✅ 성공 기준

1. 모든 인터페이스가 적절한 계층에 올바르게 배치
2. 파일명이 내용을 일관되게 반영
3. 불필요한 디렉토리 중첩 제거
4. 마이그레이션 후 모든 테스트 통과
5. 전체 코드베이스의 import 경로 업데이트

## 📦 산출물

1. Clean Architecture를 엄격히 따르는 리팩토링된 파일 구조
2. 업데이트된 import 문 (약 200개 파일 예상)
3. 통과하는 테스트 스위트
4. 명확한 마이그레이션 가이드가 포함된 PR 문서

## 🔗 관련 작업

- Spec 051: Architecture Refinement (계층적 AI 구조)
- Design Guide 012: Architecture Refinement Principles
