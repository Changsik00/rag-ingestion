# Use Case Stories for BDD Integration Tests

이 문서는 BDD 시나리오의 배경이 되는 사용자 스토리를 정의합니다.

---

## 📖 Use Case 1: 웹 콘텐츠 수집 및 저장

**Actor:** API 사용자 (개발자, 자동화 시스템)

**Goal:** 웹 페이지를 수집하여 RAG 시스템에 저장

**Preconditions:**
- API 서버가 실행 중
- Neo4j, ChromaDB가 실행 중
- 유효한 인터넷 연결

**Main Success Scenario:**
1. 사용자가 유효한 URL과 함께 POST /ingest/web 요청
2. 시스템이 Job을 생성하고 202 Accepted 반환
3. Background에서 웹 페이지 스크래핑
4. LLM을 통한 메타데이터 추출 (enable_extraction=True)
5. Neo4j와 ChromaDB에 저장
6. Job 상태가 COMPLETED로 변경
7. GET /documents로 저장된 문서 확인 가능

**Alternative Flows:**
- 2a. enable_extraction=False → 메타데이터 추출 생략
- 3a. 잘못된 URL 형식 → 400/422 에러 즉시 반환
- 3b. 존재하지 않는 URL (404) → Job FAILED
- 4a. LLM 실패 → 부분 성공 or FAILED (정책에 따름)

**Postconditions:**
- Document가 DB에 저장됨
- Job 상태가 COMPLETED or FAILED
- 에러 시 명확한 error_message 제공

---

## 📖 Use Case 2: 예외 상황 처리

**Actor:** API 사용자

**Goal:** 시스템이 다양한 예외 상황을 적절히 처리하는지 검증

**Scenarios:**

### 2.1 잘못된 입력 검증
- **When:** 잘못된 URL 형식 입력
- **Then:** 422 Unprocessable Entity, 명확한 에러 메시지

### 2.2 외부 리소스 실패
- **When:** 404, 네트워크 오류 등
- **Then:** Job FAILED, 상세한 error_message

### 2.3 특수 케이스
- **When:** 한글 URL, 매우 긴 URL 등
- **Then:** 올바른 URL encoding 처리 또는 명확한 실패 메시지

---

## 📖 Use Case 3: 동시성 및 확장성

**Actor:** 여러 API 사용자

**Goal:** 동시 요청 처리 및 Job ID 고유성 보장

**Scenario:**
1. 여러 사용자가 동시에 수집 요청
2. 각 요청이 고유한 Job ID 생성
3. 각 Job이 독립적으로 처리
4. 상호 간섭 없이 모두 완료

**Postconditions:**
- 모든 Job ID가 고유함
- 각 Job이 독립적으로 완료/실패
- Race condition 없음

---

## 🔗 Use Case와 테스트 매핑

| Use Case | BDD 테스트 파일 |
|----------|----------------|
| UC1: 웹 콘텐츠 수집 (성공) | `test_success_flows.py` |
| UC2.1-2.2: 예외 처리 | `test_failure_flows.py` |
| UC2.3, UC3: 특수 케이스 | `test_edge_cases.py` |

---

## 📝 시나리오 작성 가이드

BDD 시나리오를 작성할 때:
1. **Use Case 참조** - 어떤 UC에 속하는지 명시
2. **Given-When-Then 구조** 유지
3. **비즈니스 용어** 사용 (기술 용어 최소화)
4. **실제 사용자 행동** 시뮬레이션
5. **명확한 성공/실패 기준**
