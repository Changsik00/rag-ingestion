.PHONY: build-base up down logs test lint

# Base Image 빌드
build-base:
	docker build -t rag-ingestion-base:latest -f Dockerfile.base .

# 전체 서비스 실행 (Base Image 빌드 선행)
up: build-base
	docker compose up -d --build

# 서비스 중지
down:
	docker compose down

# 로그 확인
logs:
	docker compose logs -f

# 테스트 실행
test:
	uv run pytest

# 린트 실행
lint:
	uv run ruff check .
	uv run ruff format .
