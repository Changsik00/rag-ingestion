# Remaining Integration Test Scenarios

이 문서는 Spec 009에서 계획했지만 구현하지 못한 Integration Test 시나리오 목록입니다.
향후 별도 Spec 또는 점진적 개선 작업으로 구현해야 합니다.

---

## 📝 현재 상태 (2026-01-17)

### ✅ 구현 완료
- Contract Tests 전체 (32 passed, 2 skipped)
- Integration Test 핵심 시나리오 일부 구현 예정

### ⏳ 미구현 (이 문서에서 다룸)
- Task 6: 성공 시나리오 2개 미구현
- Task 7: 실패 시나리오 4개 미구현
- Task 8: Edge Cases 3개 미구현

---

## 🎯 Task 6: 성공 시나리오 (미구현 항목)

### ✅ 구현 예정
1. **시나리오 1: 정상적인 웹 페이지 수집 (기본 플로우)**
   - POST /ingest/web → Job 폴링 → GET /documents
   - Neo4j, ChromaDB 저장 확인

2. **시나리오 2: Extraction 비활성화 플로우**
   - enable_extraction=False
   - metadata가 비어있음 확인

### ❌ 미구현 (향후 추가 필요)

#### 시나리오 3: 중복 URL 처리 (멱등성)
**목적:** 동일한 URL을 두 번 수집했을 때 시스템이 어떻게 반응하는지 검증

**구현 가이드:**
```python
def test_duplicate_url_handling():
    """
    Given: 동일한 URL로 두 번 수집 요청
    When: 두 번째 요청이 처리되면
    Then: 적절히 처리됨 (중복 허용 or 에러)
    """
    url = "https://example.com/article"
    
    # 첫 번째 수집
    response1 = client.post("/ingest/web", json={"url": url})
    job_id_1 = response1.json()["job_id"]
    wait_for_job_completion(job_id_1)
    
    # 두 번째 수집 (동일 URL)
    response2 = client.post("/ingest/web", json={"url": url})
    job_id_2 = response2.json()["job_id"]
    wait_for_job_completion(job_id_2)
    
    # 검증: 두 Job 모두 완료되거나 적절한 중복 처리
    job1 = client.get(f"/jobs/{job_id_1}").json()
    job2 = client.get(f"/jobs/{job_id_2}").json()
    
    assert job1["status"] == "COMPLETED"
    assert job2["status"] == "COMPLETED"
    
    # Document 수 확인 (중복 정책에 따라 1개 or 2개)
    docs = client.get("/documents").json()
    # TODO: 중복 정책이 결정되면 assertion 추가
```

**의존성:**
- 중복 URL 처리 정책 결정 필요
- Document ID가 URL 기반인지, 매번 새로 생성하는지 명확히 해야 함

---

#### 시나리오 4: 다양한 콘텐츠 타입
**목적:** HTML, Markdown, 긴 텍스트 등 다양한 콘텐츠가 정상 처리되는지 검증

**구현 가이드:**
```python
@pytest.mark.parametrize("url,expected_content_type", [
    ("https://example.com/html-page", "HTML"),
    ("https://example.com/markdown.md", "Markdown"),
    ("https://example.com/long-article", "긴 텍스트 (10KB+)"),
])
def test_various_content_types(url, expected_content_type):
    """
    Given: 다양한 콘텐츠 타입의 URL
    When: 수집 요청을 보내면
    Then: 모두 정상 처리됨
    """
    response = client.post("/ingest/web", json={"url": url})
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "COMPLETED"
    
    # Document 저장 확인
    docs = client.get("/documents").json()
    doc = next((d for d in docs if d["source"]["url"] == url), None)
    assert doc is not None
    assert len(doc["content"]) > 0
```

**의존성:**
- 테스트용 mock 서버 또는 실제 테스트 URL 필요
- httpbin.org 같은 서비스 활용 가능

---

## 🚨 Task 7: 실패 시나리오 (미구현 항목)

### ✅ 구현 예정
1. **시나리오 1: 잘못된 URL 형식 → 400 에러**
2. **시나리오 2: 존재하지 않는 URL (404) → Job FAILED**
3. **시나리오 5: LLM 호출 실패 (Mock) → 적절한 처리**

### ❌ 미구현 (향후 추가 필요)

#### 시나리오 3: 타임아웃 시뮬레이션
**목적:** 매우 느린 응답이 올 때 Job이 적절히 실패하는지 검증

**구현 가이드:**
```python
def test_timeout_handling(mocker):
    """
    Given: 매우 느린 응답을 주는 URL
    When: 수집 요청을 보내면
    Then: 타임아웃으로 Job FAILED, 명확한 에러 메시지
    """
    import requests
    
    # requests.get을 Mock하여 타임아웃 발생시키기
    mocker.patch('requests.get', side_effect=requests.Timeout("Connection timeout"))
    
    response = client.post("/ingest/web", json={"url": "https://slow-server.example.com"})
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "FAILED"
    assert "timeout" in job.get("error", "").lower()
```

**의존성:**
- Scraper에 timeout 설정 필요 (현재 없음)
- requests.get(timeout=30) 같은 설정 추가

---

#### 시나리오 4: 접근 불가능한 URL (네트워크 오류)
**목적:** 존재하지 않는 도메인에 대한 처리 검증

**구현 가이드:**
```python
def test_network_error_handling():
    """
    Given: 존재하지 않는 도메인
    When: 수집 요청을 보내면
    Then: Job FAILED, connection error 메시지
    """
    response = client.post("/ingest/web", json={
        "url": "https://this-domain-does-not-exist-12345678.com"
    })
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "FAILED"
    assert "connection" in job.get("error", "").lower() or "dns" in job.get("error", "").lower()
```

---

#### 시나리오 6: 잘못된 Job ID 조회 → 404
**목적:** 존재하지 않는 Job ID 조회 시 명확한 에러 반환

**구현 가이드:**
```python
def test_invalid_job_id_returns_404():
    """
    Given: 존재하지 않는 Job ID
    When: GET /jobs/{job_id} 요청
    Then: 404 Not Found 반환
    """
    response = client.get("/jobs/non-existent-job-id-12345")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

**의존성:** 현재 API 구현 확인 필요 (404 반환하는지, 500 반환하는지)

---

#### 시나리오 7: 빈 콘텐츠 처리
**목적:** 빈 HTML 페이지가 왔을 때 적절한 처리

**구현 가이드:**
```python
def test_empty_content_handling(mocker):
    """
    Given: 빈 HTML 페이지 (<html></html>)
    When: 수집 요청을 보내면
    Then: 적절히 처리 (에러 or 빈 document)
    """
    import requests
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.text = "<html></html>"
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html"}
    
    mocker.patch('requests.get', return_value=mock_response)
    
    response = client.post("/ingest/web", json={"url": "https://empty-page.example.com"})
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    # TODO: 정책 결정 필요 - FAILED? or COMPLETED with empty content?
    # assert job["status"] == "FAILED"  # or "COMPLETED"
```

**의존성:** 빈 콘텐츠 처리 정책 결정 필요

---

## 🎲 Task 8: Edge Cases (미구현 항목)

### ✅ 구현 예정
1. **시나리오 2: 특수 문자가 포함된 URL (한글, 공백)**
2. **시나리오 5: 동시 다발적 요청 (Concurrency)**

### ❌ 미구현 (향후 추가 필요)

#### 시나리오 1: 매우 긴 URL
**목적:** 극단적으로 긴 URL에 대한 처리

**구현 가이드:**
```python
def test_very_long_url():
    """
    Given: 1000자 이상의 긴 URL
    When: 수집 요청을 보내면
    Then: 적절히 처리 (성공 or 명확한 에러)
    """
    long_url = "https://example.com/" + "a" * 1000 + "/page"
    
    response = client.post("/ingest/web", json={"url": long_url})
    
    # 414 URI Too Long or 202 Accepted
    assert response.status_code in [202, 400, 414]
    
    if response.status_code == 202:
        job_id = response.json()["job_id"]
        wait_for_job_completion(job_id)
        job = client.get(f"/jobs/{job_id}").json()
        # 성공 or 실패 둘 다 가능, 명확한 상태만 확인
        assert job["status"] in ["COMPLETED", "FAILED"]
```

---

#### 시나리오 3: 매우 큰 HTML 페이지 (10MB+)
**목적:** 메모리 오버플로우 없이 큰 페이지 처리

**구현 가이드:**
```python
def test_large_html_page(mocker):
    """
    Given: 10MB 이상의 큰 HTML 페이지
    When: 수집 요청을 보내면
    Then: 메모리 오버플로우 없이 처리
    """
    import requests
    from unittest.mock import Mock
    
    # 10MB HTML 생성
    large_html = "<html><body>" + ("x" * 10 * 1024 * 1024) + "</body></html>"
    
    mock_response = Mock()
    mock_response.text = large_html
    mock_response.status_code = 200
    
    mocker.patch('requests.get', return_value=mock_response)
    
    response = client.post("/ingest/web", json={"url": "https://large-page.example.com"})
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] in ["COMPLETED", "FAILED"]
    # 실패했다면 명확한 에러 메시지
    if job["status"] == "FAILED":
        assert "size" in job.get("error", "").lower() or "memory" in job.get("error", "").lower()
```

**의존성:** 
- 최대 콘텐츠 크기 제한 정책 필요
- 메모리 모니터링 추가 고려

---

#### 시나리오 4: Redirect 처리 (301/302)
**목적:** HTTP Redirect가 정상적으로 따라가는지 검증

**구현 가이드:**
```python
def test_redirect_handling():
    """
    Given: 301 Redirect하는 URL
    When: 수집 요청을 보내면
    Then: 최종 URL로 정상 수집됨
    """
    # httpbin.org/redirect-to 같은 서비스 활용
    redirect_url = "https://httpbin.org/redirect-to?url=https://example.com&status_code=301"
    
    response = client.post("/ingest/web", json={"url": redirect_url})
    job_id = response.json()["job_id"]
    
    wait_for_job_completion(job_id)
    
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "COMPLETED"
    
    # 최종 source_url이 https://example.com인지 확인
    docs = client.get("/documents").json()
    # TODO: source_url이 redirect 후 URL을 저장하는지 확인
```

**의존성:**
- requests.get이 기본적으로 redirect를 따라감 (allow_redirects=True)
- 정책: 최종 URL vs 원본 URL 중 어느 것을 저장할지 결정

---

## 📋 구현 우선순위

### High Priority (빠른 시일 내 구현)
1. **잘못된 Job ID 조회 → 404** (시나리오 7-6)
   - API 안정성에 중요
   - 구현 간단

2. **중복 URL 처리** (시나리오 6-3)
   - 실제 사용 시 자주 발생할 수 있는 케이스
   - 정책 결정 필요

### Medium Priority
3. **타임아웃 처리** (시나리오 7-3)
   - 실제 운영 환경에서 중요
   - Scraper 수정 필요

4. **Redirect 처리** (시나리오 8-4)
   - 실제 웹에서 흔한 케이스

### Low Priority (선택적 구현)
5. **매우 긴 URL** (시나리오 8-1)
6. **매우 큰 HTML** (시나리오 8-3)
7. **빈 콘텐츠** (시나리오 7-7)
8. **다양한 콘텐츠 타입** (시나리오 6-4)

---

## 🔗 관련 문서

- `docs/testing_strategy.md` - 전체 테스트 전략
- `specs/009-testing-strategy/spec.md` - 요구사항
- `specs/009-testing-strategy/plan.md` - 원래 계획
- `specs/009-testing-strategy/task.md` - 진행 상황

---

## 📝 향후 작업 시 체크리스트

미구현 시나리오를 추가할 때:
- [ ] 정책 결정 필요 사항 확인
- [ ] 의존성 (Scraper, API 변경) 확인
- [ ] 테스트 작성
- [ ] 실제 코드 수정 (필요 시)
- [ ] 문서 업데이트 (이 파일에서 항목 제거)
