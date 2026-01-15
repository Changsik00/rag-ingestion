# Getting Started

## Prerequisites
- **Python**: 3.9+
- **uv**: Package manager (Required)

## Installation

1. 의존성 설치
```bash
uv sync
```

## Service Ports
각 서비스는 포트 충돌을 방지하기 위해 아래 포트를 기본값으로 사용합니다. `uvicorn` 실행 시 기본 포트(8000)를 사용하므로, ChromaDB는 8001로 우회 설정되어 있습니다.

| Service | Port | Description |
| :--- | :--- | :--- |
| **API Server (FastAPI)** | `8000` | 메인 애플리케이션 (Default) |
| **ChromaDB** | `8001` | Vector DB (충돌 방지용) |
| **Neo4j (HTTP)** | `7474` | Graph DB Browser |
| **Neo4j (Bolt)** | `7687` | Graph DB Connection |

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
