# Refactor: 클린 아키텍처 계층 정제 (Spec 052)

## 🎯 목표
클린 아키텍처 원칙을 엄격히 준수하기 위해 계층 경계와 네이밍 규칙을 정제합니다. 이 PR은 Spec 051 이후 식별된 기술 부채를 해결하며, 일관된 계층 배치와 명확한 네이밍에 초점을 맞춥니다.

## 🛠 주요 변경 사항

### 1. 아키텍처 계층 교정
- **인터페이스 이동**: `LLMInterface`와 `ScraperInterface`를 `domain`에서 `application/interfaces`로 이동했습니다. (애플리케이션이 필요로 하는 인터페이스 정의).
- **서비스 이동**: `Feedback` 서비스를 `domain`에서 `application/services`로 이동했습니다.
- **Value Objects**: `DocumentMetadata`를 `domain/value_objects`로 이동했습니다.

### 2. 네이밍 및 구조 표준화
- **Agent 이름 변경**: `admin_agent.py` → `agent.py`. "관리자" 기능에 국한되지 않는 일반적인 대화형 에이전트임을 반영했습니다.
- **서비스 클래스 이름 변경**: `IngestionUseCase` → `Ingestion`. `Integrity`, `Feedback` 등 다른 서비스와 네이밍을 통일했습니다.
- **Core 리팩토링**: `core/utils/`를 `core/`로 평탄화하고 `logging_config.py`를 `logger.py`로 변경했습니다.
- **State 명확화**: `ingestion`과 `rag` 도메인의 `state.py`를 `graph_state.py`로 변경하여 모호성을 제거했습니다.

### 3. 코드 정리
- 레거시 중복 API 엔드포인트 파일 제거: `app/interfaces/api/endpoints/jobs.py`.
- 모든 관련 Import 문 업데이트 완료.

## ✅ 검증
- **테스트**: 194개 테스트 전수 통과.
- **Linting**: `ruff` 체크 및 포맷팅 통과.

## 🔗 관련 문서
- **Spec 052**: Clean Architecture Layer Refinement
- **Spec 051**: Architecture Refinement (Consistency & Cleanliness)
