# Spec 018: System Stability & Test Refactoring

## 1. Background

이전 단계(Spec 017)까지 기능 구현에 집중하면서, 시스템 전반의 예외 처리와 테스트 안정성이 저하되었습니다. "System Stability Audit" 결과, 다음과 같은 주요 위험 요소가 식별되었습니다.

1.  **Blanket Exception Handling**: `IngestionService`에서 모든 예외를 잡아서 실패 처리하므로, 재시도 가능한 에러와 치명적 에러가 구분되지 않음.
2.  **Null Safety Risks**: `Repo.get()` 메서드 등에서 `None` 반환 시 클라이언트 코드(Service)에서 `AttributeError`가 발생할 위험이 있음.
3.  **Skipped Tests**: 통합 테스트 4개가 환경 설정 문제 등으로 `@pytest.mark.skip` 처리되어 있어 회귀 감지가 불가능함.
4.  **Anti-patterns**: `print()` 사용, 테스트 코드 내 `try-except` 사용 등.

안정적인 Phase 4(Automation) 진입을 위해, 기술 부채를 청산하고 견고한 Foundation을 구축해야 합니다.

## 2. Objectives

시스템의 예측 가능성과 회복 탄력성(Resilience)을 확보하고, 테스트 신뢰도를 100%로 복구합니다.

*   **Refactor Exception Handling**: 명시적인 Custom Exception(`DomainException`, `InfraException`)을 정의하고 처리합니다.
*   **Harden Repositories**: Null Safety를 보장하고, 필요한 경우 Transaction을 적용합니다.
*   **Restore Tests**: Skipped 테스트를 모두 수정하여 활성화하고, Test Anti-pattern(try-except assert)을 제거합니다.
*   **Logging**: `print()`를 제거하고 표준 `logging` 모듈을 적용합니다.

## 3. Scope & Requirements

### 3.1 Custom Exception Hierarchy
*   `app/core/exceptions.py` 신설
    *   `DoitException` (Base)
    *   `DomainException` (Business Logic)
    *   `InfrastructureException` (DB, External API)
    *   `ScrapingException`, `LLMException` 등 세분화

### 3.2 Ingestion Service Handling
*   `ingestion.py`의 `process_job` 로직 수정
    *   `try-except Exception` 제거
    *   `RecoverableException` (Network, Timeout) -> 작업 상태 유지 또는 Retry 메커니즘(추후)
    *   `NonRecoverableException` (Logic, Data) -> `FAILED`
    *   Standard Logging 적용 (`logger.error`, `logger.info`)

### 3.3 Repository Hardening
*   **Neo4jStorage & ChromaStorage**
    *   `get()` 메서드가 데이터 부재 시 명시적으로 `None` 반환 (기존 로직 재검증).
    *   `save()` 메서드 내 데이터 누락(Missing fields) 방어 로직 추가.
    *   Database connection 에러 발생 시 `InfrastructureException` 래핑하여 전파.

### 3.4 Test Restoration
*   **Disabled Tests 복구**:
    *   `tests/integration/bdd/test_failure_flows.py`
    *   `tests/integration/bdd/test_entity_relationships.py`
    *   `tests/contracts/test_storage_contract.py`
    *   환경 변수 Mocking 또는 Docker 서비스 의존성 해결을 통해 Skip 제거.
*   **Bad Test Patterns 수정**:
    *   `tests/unit/test_scraper.py`: `try-except` 블록 대신 `pytest.raises` 사용.

## 4. Constraints

*   기존 기능(Ingestion Flow)의 동작 변경 없음.
*   외부 라이브러리 추가 없음 (Python 표준 `logging` 사용).
*   모든 테스트는 `PASSED` 상태여야 함.
