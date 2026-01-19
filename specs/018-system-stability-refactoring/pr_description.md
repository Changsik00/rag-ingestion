# refactor(spec-018): system stability and test restoration

## 📋 Summary
본 PR은 **Spec 018: System Stability & Test Refactoring**을 구현하여 시스템의 전반적인 안정성을 강화하고, 기존에 스킵되었던 테스트를 복구했습니다.
주요 변경 사항은 **Custom Exception Hierarchy 도입**, **구조화된 로깅 적용**, 그리고 **Integration Test의 Mocking 전략 개선**입니다.

### Before & After
- **Exceptions:** `try-except Exception`의 모호한 에러 처리 -> `DoitException` 계층(`Domain`, `Infrastructure`)을 통한 명확한 에러 구분.
- **Logging:** `print()` 문의 혼재 -> `app.core.logging_config`를 통한 표준화된 로그 포맷 및 레벨링.
- **Tests:** `test_llm_failure...` 등 주요 통합 테스트 Skip -> `dependency_overrides`와 수동 주입을 활용하여 100% 복구 및 안정화.

## 🎯 Key Review Points
1. **Custom Exception Hierarchy (`app/core/exceptions.py`)**
   - 시스템 전반에서 사용할 `DoitException`과 하위 클래스들의 구조가 적절한지 확인 부탁드립니다.
2. **Ingestion Failure Handling (`app/use_cases/ingestion.py`)**
   - LLM 추출 실패 시 Job이 `FAILED`가 아닌 `COMPLETED` (Partial Success)로 처리되는 로직이 의도와 부합하는지 검토 바랍니다.
3. **Integration Test Strategies (`tests/integration/bdd/test_failure_flows.py`)**
   - `IngestionService`에 대한 `dependency_overrides` 적용 시, `@lru_cache` 및 DI 문제를 해결하기 위해 `IngestionService` 자체를 재조립하여 Mock을 주입한 방식이 적절한지 확인해주세요.
4. **Unit Test Implementation (`tests/unit/test_storage.py`)**
   - Neo4j Session Context Manager(`__enter__`)를 모킹하기 위해 `MagicMock`을 도입한 부분.

## 🧪 Verification
### Automated Tests
```bash
uv run pytest -v
# Result: 110 passed, 0 failed, 3 skipped, 27 warnings
```

### Manual Verification
- **Log Inspection**: 에러 발생 시 Stack Trace가 로그에 정형화된 포맷으로 남는 것을 확인했습니다.
- **Graph State**: LLM 실패 시에도 Document 노드가 Neo4j/Chroma에 정상적으로 생성됨을 확인했습니다.

## 📦 Files Changed

### 🆕 New Files
- `app/core/exceptions.py`: 공통 예외 클래스 정의.
- `app/core/logging_config.py`: 로깅 설정 유틸리티.

### 🛠 Modified Files
- `app/use_cases/ingestion.py`: 예외 처리 리팩토링 및 로깅 적용.
- `app/infrastructure/storage/chroma.py`, `neo4j_document_repository.py`: 인프라스트럭처 예외 래핑 및 Null check 강화.
- `tests/integration/bdd/test_failure_flows.py`: LLM 실패 시나리오 테스트 복구 (Mocking 개선).
- `tests/integration/bdd/test_entity_relationships.py`: `requests` 제거 및 `TestClient`로 리팩토링.
- `tests/unit/test_scraper.py`: Anti-pattern(`try-except`) 제거 및 `pytest.raises` 적용.
- `tests/unit/test_storage.py`: Context Manager Mocking 추가.

### 🗑 Deleted Files
- (None)

**Total:** 8 files changed

## ✅ Definition of Done
- [x] 모든 Unit/Integration Test 통과 (110 passed)
- [x] Custom Exception 적용 및 기존 코드 리팩토링 완료
- [x] Logging 시스템 표준화
- [x] Skipped Test 복구 완료
