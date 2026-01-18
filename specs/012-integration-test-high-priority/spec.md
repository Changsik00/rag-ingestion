# Spec 012: Integration Test Scenarios - High Priority

## 🎯 목표

Spec 009에서 미구현된 Integration Test 시나리오 중 **High Priority** 2개를 구현하여 시스템 안정성을 향상시킵니다.

---

## 🔍 배경

Spec 009에서 Contract Tests와 기본 Integration Tests를 구현했지만, 실제 운영 환경에서 발생할 수 있는 중요한 시나리오들이 미구현 상태입니다.

**미구현 시나리오:** 9개 (성공 2개, 실패 4개, Edge Case 3개)  
**이번 Spec:** High Priority 2개만 선별 구현

---

## 📋 요구사항

### 1️⃣ 잘못된 Job ID 조회 → 404 (High Priority)

**현재 문제:**
- 존재하지 않는 Job ID를 조회하면 어떤 응답이 오는지 불명확
- 500 에러가 발생할 가능성

**요구사항:**
```python
def test_invalid_job_id_returns_404():
    """
    Given: 존재하지 않는 Job ID
    When: GET /jobs/{job_id} 요청
    Then: 404 Not Found 반환, 명확한 에러 메시지
    """
    response = client.get("/jobs/non-existent-job-id-12345")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

**필요 작업:**
- API 엔드포인트 수정 (존재하지 않는 Job → HTTPException(404))
- Integration Test 추가

---

### 2️⃣ 중복 URL 처리 - 멱등성 (High Priority)

**현재 문제:**
- 동일 URL을 두 번 수집하면 어떻게 되는지 정책 없음
- Document ID 생성 방식 불명확 (UUID 랜덤 vs URL 기반)

**요구사항:**
```python
def test_duplicate_url_handling():
    """
    Given: 동일한 URL로 두 번 수집 요청
    When: 두 번째 요청이 처리되면
    Then: 
      - Option A: 두 Job 모두 COMPLETED, 2개 Document 생성 (현재 방식)
      - Option B: 두 Job 모두 COMPLETED, 1개 Document만 유지 (중복 제거)
    """
```

**정책 결정 필요:**
1. **현재 방식 유지 (Option A):**
   - 매번 새로운 UUID로 Document 생성
   - 동일 URL도 별도 Document
   - 장점: 시간대별 콘텐츠 변화 추적 가능
   - 단점: 중복 데이터 증가

2. **중복 제거 (Option B):**
   - URL을 기준으로 Document ID 생성 (Hash)
   - 동일 URL → 기존 Document 업데이트
   - 장점: 스토리지 효율적
   - 단점: 과거 버전 손실

**이번 Spec:**
- **Option A 채택** (현재 방식 검증)
- 테스트로 동작 확인만 수행
- 향후 Spec에서 중복 정책 개선 가능

---

## ✅ Acceptance Criteria

### Scenario 1: Invalid Job ID
1. ✅ 존재하지 않는 Job ID 조회 시 404 반환
2. ✅ 명확한 에러 메시지 ("Job not found")
3. ✅ Integration Test 통과

### Scenario 2: Duplicate URL
1. ✅ 동일 URL 두 번 수집 시 두 Job 모두 COMPLETED
2. ✅ 2개의 별도 Document 생성 확인
3. ✅ Integration Test 통과

### General
1. ✅ 기존 테스트 모두 통과 (45+ passed)
2. ✅ Ruff lint 에러 없음

---

## ⚠️ Breaking Changes

**없음** - 기존 동작 유지, 테스트 추가 및 404 에러 핸들링만 개선

---

## 🔮 Future Work

**Medium Priority (다음 Spec):**
- 타임아웃 처리
- 네트워크 오류 처리
- Redirect 처리

**Low Priority:**
- 빈 콘텐츠 처리
- 매우 큰 HTML
- 다양한 콘텐츠 타입

---

**작성일:** 2026-01-18  
**우선순위:** High  
**예상 소요 시간:** 2-3시간
