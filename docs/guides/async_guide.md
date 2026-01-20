# Async Processing & Concurrency Guide
> **Note for JavaScript Developers**: Python의 `async/await`는 JS와 비슷해 보이지만, 동작 방식과 주의할 점(Blocking I/O)에서 결정적인 차이가 있습니다. 이 문서는 이번 프로젝트의 리팩토링 배경과 그 기술적 이유를 설명합니다.

## 1. 배경: 무엇이 문제였나?

### 기존 구조 (Synchronous Blocking)
```python
@app.post("/ingest/web")
async def ingest(url: str):
    # 1. requests.get(url) 호출 -> 응답 올 때까지 30초 대기
    # 2. 이 30초 동안 서버(Event Loop)는 멈춤!
    # 3. 다른 사용자의 로그인 요청도 30초간 처리 불가
    service.ingest(url) 
    return "OK"
```

### JS 개발자가 빠지기 쉬운 함정
JavaScript(Node.js)에서는 `fs.readFile`이나 `axios.get`을 쓰면 기본적으로 Non-blocking으로 동작하여 메인 스레드를 막지 않습니다.
하지만 **Python**에서는:
1.  `async def`를 선언했더라도,
2.  내부에서 `requests`나 표준 `db driver` 같은 **동기(Synchronous) 라이브러리**를 쓰면,
3.  **Event Loop 전체가 차단(Block)**됩니다. (마치 JS에서 `fs.readFileSync`를 쓴 것과 동일)

## 2. 해결책: Spec 004의 아키텍처 변화

우리는 두 가지 문제를 해결해야 했습니다.
1.  **Client Timeout**: 사용자가 30초씩 기다리게 하지 말 것. (UX 문제)
2.  **Server Blocking**: 한 명의 요청 때문에 서버 전체가 멈추지 않게 할 것. (성능 문제)

### 변경된 구조 (Async Fire-and-Forget)

```python
@app.post("/ingest/web", status_code=202)
async def ingest_web_page(background_tasks: BackgroundTasks):
    # 1. 접수 (DB Insert) - 매우 빠름
    job = service.create_job(...)
    
    # 2. 처리 위임 (BackgroundTasks)
    # -> FastAPI가 응답을 보낸 "직후"에 별도 컨텍스트에서 실행함
    background_tasks.add_task(service.process_job, job.job_id)
    
    # 3. 즉시 응답 (202 Accepted)
    return {"job_id": job.job_id}
```

## 3. Implementation Details (코드 레벨 설명)

### A. 서비스 계층 분리 (`ingestion.py`)
거대했던 `ingest` 메서드를 책임에 따라 둘로 쪼갰습니다.

| 메서드 | 역할 | 실행 시점 | 특징 |
| :--- | :--- | :--- | :--- |
| **`create_job()`** | 주문 접수 | API 요청 즉시 | DB에 `PENDING` 상태 기록. 순식간에 끝남. |
| **`process_job()`** | 요리(처리) | 응답 반환 후 | 실제 `Scraping`(오래 걸림). 에러 시 `FAILED` 기록. |

### B. Blocking I/O 처리
현재 우리 프로젝트는 `requests`(스크래퍼)와 `neo4j`(DB) 드라이버가 모두 **동기(Sync)** 방식입니다.
따라서 `BackgroundTasks`로 넘긴 것은 신의 한 수 였습니다.
- 메인 API 응답 스레드는 즉시 해방됩니다.
- 백그라운드에서 동기 코드가 돌더라도, 사용자는 이미 응답을 받았으므로 영향을 받지 않습니다.

> **Future Work**: 진정한 고성능을 위해서는 내부 라이브러리도 `httpx`(Async Client)나 `neo4j` Async Driver로 교체하는 것이 좋습니다. 하지만 현재 구조(BackgroundTasks)만으로도 "사용자 경험"과 "서버 응답성" 문제는 90% 이상 해결되었습니다.

## 4. 요약
- **JavaScript vs Python**: Python `async` 함수 안에서 동기 라이브러리를 쓰면 서버가 멈춘다(Blocking).
- **해결**: 오래 걸리는 작업은 `BackgroundTasks`로 미루고, 클라이언트에게는 "접수증(Job ID)"만 주고 즉시 보낸다.
- **결과**: 타임아웃 없는 대량 처리 가능, 서버 가용성 확보.
