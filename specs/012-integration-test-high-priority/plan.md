# Implementation Plan: Spec 012 - Integration Test High Priority

## 📋 Summary

Spec 009에서 미구현된 Integration Test 중 High Priority 2개를 구현합니다.

**주요 발견:**
- ✅ Invalid Job ID → 404는 **이미 구현됨!** (`jobs.py` Line 24-30)
- ✅ 테스트만 추가하면 됨

**작업 내용:**
1. Invalid Job ID 테스트 추가 (이미 구현된 기능 검증)
2. Duplicate URL 테스트 추가 (현재 동작 확인)

---

## 🔍 Current Implementation Review

### GET /jobs/{job_id} - 이미 구현됨 ✅

```python
# app/interfaces/api/endpoints/jobs.py:19-30
@router.get("/{job_id}", response_model=IngestionJob)
async def get_job(
    job_id: str,
    repo: JobRepository = Depends(get_job_repository)
):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    return job
```

**결론:** API는 이미 올바르게 구현됨. 테스트만 추가!

---

## 📝 Proposed Changes

### 1. Integration Test 추가

#### [NEW] `tests/integration/bdd/test_high_priority_scenarios.py`

**테스트 1: Invalid Job ID**
```python
def test_invalid_job_id_returns_404():
    """
    Given: 존재하지 않는 Job ID
    When: GET /jobs/{job_id} 요청
    Then: 404 Not Found, 명확한 에러 메시지
    """
    response = requests.get(f"{BASE_URL}/jobs/non-existent-job-id-12345")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

**테스트 2: Duplicate URL - Sequential**
```python
def test_duplicate_url_sequential_ingestion():
    """
    Given: 동일한 URL로 두 번 순차적으로 수집 요청
    When: 두 Job이 완료되면
    Then: 
      - 두 Job 모두 COMPLETED 상태
      - 2개의 별도 Document 생성됨
    """
    url = "https://httpbin.org/html"
    
    # 첫 번째 수집
    response1 = requests.post(f"{BASE_URL}/ingest/web", json={"url": url})
    job_id_1 = response1.json()["job_id"]
    
    # 완료 대기
    wait_for_job_completion(job_id_1)
    
    # 두 번째 수집 (동일 URL)
    response2 = requests.post(f"{BASE_URL}/ingest/web", json={"url": url})
    job_id_2 = response2.json()["job_id"]
    
    # 완료 대기
    wait_for_job_completion(job_id_2)
    
    # 검증
    job1 = get_job_status(job_id_1)
    job2 = get_job_status(job_id_2)
    
    assert job1["status"] == "COMPLETED"
    assert job2["status"] == "COMPLETED"
    
    # Document 2개 생성 확인
    docs = requests.get(f"{BASE_URL}/documents?limit=100").json()
    matching_docs = [d for d in docs if d["source"]["url"] == url]
    assert len(matching_docs) >= 2  # 최소 2개
```

**Helper Function:**
```python
def wait_for_job_completion(job_id: str, timeout: int = 30) -> None:
    """Job이 COMPLETED or FAILED 될 때까지 대기"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        job = get_job_status(job_id)
        if job["status"] in ["COMPLETED", "FAILED"]:
            return
        time.sleep(1)
    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

def get_job_status(job_id: str) -> dict:
    """Job 상태 조회"""
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    response.raise_for_status()
    return response.json()
```

---

## 🧪 Verification Plan

### Automated Tests

**1. Run New Integration Tests**
```bash
# Docker 실행
docker compose up -d

# Integration Tests 실행
uv run pytest tests/integration/bdd/test_high_priority_scenarios.py -v -m integration

# 예상 결과: 2 passed
```

**2. Run All Integration Tests**
```bash
uv run pytest tests/integration/ -v -m integration

# 예상 결과: 기존 테스트 + 2개 추가 = 모두 통과
```

**3. Run All Tests (Contract + Unit + Integration)**
```bash
uv run pytest tests/ -v

# 예상 결과: 47+ passed, 2 skipped
```

### Manual Verification

**1. Invalid Job ID 수동 테스트**
```bash
# Docker 실행 중
curl http://localhost:8000/jobs/non-existent-id

# 예상 결과:
# Status: 404
# Body: {"detail":"Job non-existent-id not found"}
```

**2. Duplicate URL 수동 테스트**
```bash
# 첫 번째 수집
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://httpbin.org/html"}'
# 응답: {"job_id":"job-1-id","status":"PENDING"}

# 두 번째 수집 (동일 URL)
curl -X POST "http://localhost:8000/ingest/web" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://httpbin.org/html"}'
# 응답: {"job_id":"job-2-id","status":"PENDING"}

# Job 상태 확인 (모두 COMPLETED)
curl http://localhost:8000/jobs/job-1-id
curl http://localhost:8000/jobs/job-2-id

# Document 개수 확인
curl http://localhost:8000/documents?limit=100
# 응답: 동일 URL Document 2개 이상 존재
```

---

## 📊 File Changes Summary

**신규 (1개):**
- `tests/integration/bdd/test_high_priority_scenarios.py` (테스트 2개)

**수정:** 없음 (기능은 이미 구현됨)

---

## 💭 Decision Notes

### 1. 중복 URL 정책

**현재 동작:** 매번 새로운 Document 생성 (UUID 기반)

**정책 결정:**
- ✅ **Option A 채택:** 현재 방식 유지
- 이유:
  - 시간대별 콘텐츠 변화 추적 가능
  - Breaking Change 없음
  - 향후 Spec에서 중복 제거 정책 추가 가능

**향후 개선 (Icebox):**
- Document ID를 URL Hash 기반으로 변경
- `updated_at` 필드로 버전 관리
- 옵션: `keep_history=True/False`

### 2. Invalid Job ID 테스트 위치

**위치:** `tests/integration/bdd/test_high_priority_scenarios.py`

**이유:**
- BDD 스타일로 Given-When-Then 명확
- 실패 시나리오와 분리
- High Priority 시나리오만 모음

---

## ⏱️ 예상 소요 시간

- 테스트 파일 작성: 30분
- 테스트 실행 및 검증: 20분
- 문서화 및 PR: 10분

**Total:** ~1시간

---

**작성일:** 2026-01-18  
**관련 파일:**
- `specs/009-testing-strategy/remaining_scenarios.md` (참조)
- `app/interfaces/api/endpoints/jobs.py` (이미 구현됨)
