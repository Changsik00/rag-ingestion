FROM python:3.12-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# UV 설정: hardlink 실패 방지 (Docker 환경)
ENV UV_LINK_MODE=copy

# 의존성 설치 (uv 사용)
RUN uv sync --frozen --no-dev

# Admin 코드만 복사
COPY admin/ ./admin/

# Streamlit 실행
CMD ["uv", "run", "streamlit", "run", "admin/dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]
