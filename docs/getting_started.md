# Getting Started

## Prerequisites
- **Python**: 3.9+
- **uv**: Package manager (Required)

## Installation

1. 의존성 설치
```bash
uv sync
```

## Running the Server

FastAPI 서버를 개발 모드(Re-load enabled)로 실행합니다.

```bash
uv run uvicorn app.interfaces.api.main:app --reload
```
- API Docs: http://localhost:8000/docs

## Running Tests

전체 테스트를 실행합니다.

```bash
PYTHONPATH=. uv run pytest
```

---
### Manual Testing (Curl)

서버가 켜진 상태에서 아래 명령어로 수집 테스트를 할 수 있습니다.

```bash
curl -X POST "http://localhost:8000/ingest/web" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```
