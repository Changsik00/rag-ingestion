# Spec 009: Testing Strategy Improvement

## 📌 배경 (Background)

**문제 인식:**
- Spec 008 (Docker Integration Bugfix)에서 발견된 버그들이 단위 테스트 단계에서 감지되지 않음
- 통합 환경에서만 발견되는 버그들:
  - `Neo4jStorage` 생성자 파라미터 불일치 (인터페이스 계약 위반)
  - Import 오류 (모듈 구조 변경 시 놓친 참조)
  - 런타임 의존성 주입 실패

**근본 원인:**
- 단위 테스트의 User Case Coverage 부족
- Interface와 Implementation 간의 계약 검증 부재
- 실제 런타임 환경을 재현하는 Integration Test 시나리오 부족
- Mock 환경과 실제 환경의 불일치

**목표:**
- Contract Testing 도입으로 인터페이스-구현체 계약 보장
- Integration Test 시나리오 강화로 런타임 버그 조기 발견
- 테스트 전략 문서화로 향후 Spec의 테스트 품질 보증

---

## 🎯 요구사항 (Requirements)

### 1. 테스트 전략 문서 작성

**`docs/testing_strategy.md` 생성:**
- **테스트 피라미드:** Unit / Integration / E2E 각 레벨의 목적과 비중
- **Contract Testing 가이드:** 인터페이스-구현체 계약 검증 방법
- **Integration Test 원칙:** 실제 런타임 환경 재현 전략
- **Spec별 테스트 체크리스트:** 새로운 Spec 구현 시 필수 테스트 항목
- **CI 테스트 전략:** 각 테스트 레벨의 실행 시점 및 실패 처리

### 2. Contract Testing 인프라 구축

**`tests/contracts/` 디렉토리 생성:**
- Storage Contract Tests:
  - `test_storage_contract.py`: 모든 `DocumentRepository` 구현체가 동일한 계약 준수 검증
  - `test_job_repository_contract.py`: 모든 `JobRepository` 구현체 검증
- LLM Contract Tests:
  - `test_llm_contract.py`: 모든 `LLM` 인터페이스 구현체 검증
- Scraper Contract Tests:
  - `test_scraper_contract.py`: 모든 `Scraper` 구현체 검증

**검증 항목:**
- 인터페이스 준수 여부
- 생성자 시그니처 일관성
- 메서드 시그니처 일관성
- 예외 처리 일관성

### 3. Integration Test 시나리오 강화

**E2E 시나리오 테스트 추가:**
- `tests/integration/scenarios/test_full_ingestion_flow.py`:
  - 실제 사용자 행동 재현 (POST /ingest/web → Job Polling → GET /documents)
  - 실제 Neo4j, ChromaDB 사용 (Testcontainers 활용)
  - Job 상태 전이 검증 (PENDING → RUNNING → COMPLETED)

**DI Container 검증:**
- `tests/integration/test_dependency_injection.py`:
  - FastAPI dependencies가 실제로 올바른 객체 반환하는지 검증
  - 모든 인프라 컴포넌트가 실제 환경에서 초기화 가능한지 검증

---

## 🚫 비-요구사항 (Non-Requirements)

- 기존 테스트 코드의 전면 수정 (점진적 개선)
- Admin Dashboard UX 개선 (별도 Spec 010으로 분리)
- 테스트 커버리지 100% 달성 (현실적인 목표 설정)

---

## ✅ 성공 기준 (Success Criteria)

1. **문서화:**
   - [ ] `docs/testing_strategy.md` 작성 완료
   - [ ] 테스트 전략이 명확히 문서화되어 향후 Spec 작성 시 참조 가능

2. **Contract Tests:**
   - [ ] `tests/contracts/` 디렉토리 생성 및 4개 Contract Test 구현
   - [ ] 모든 Contract Test 통과

3. **Integration Tests:**
   - [ ] E2E 시나리오 테스트 1개 이상 작성
   - [ ] Testcontainers 기반 실제 DB 연동 테스트 구현
   - [ ] DI Container 검증 테스트 추가

4. **검증:**
   - [ ] 모든 기존 테스트 통과
   - [ ] 새로운 Contract Tests 통과
   - [ ] CI 파이프라인에서 정상 동작

---

## 📊 예상 영향 (Impact)

**긍정적 영향:**
- 런타임 버그 조기 발견으로 통합 환경 디버깅 시간 단축
- 인터페이스 변경 시 구현체 불일치 자동 감지
- 테스트 전략 문서화로 팀 전체의 테스트 품질 향상
- 리팩토링 안전성 증가

**Trade-offs:**
- 초기 테스트 인프라 구축 시간 소요
- CI 파이프라인 실행 시간 약간 증가 (Integration Tests)

---

## 📚 참고 자료 (References)

- [Testing Pyramid - Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Contract Testing - Pact](https://docs.pact.io/)
- [Python Protocol (PEP 544)](https://peps.python.org/pep-0544/)
- [Testcontainers Python](https://testcontainers-python.readthedocs.io/)
