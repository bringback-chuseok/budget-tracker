# 베이스 이미지
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 필수 패키지 설치 (uv 실행 및 빌드 도구 등)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# 의존성 설치 단계: 캐시 최적화
COPY pyproject.toml uv.lock* /app/
RUN uv venv && uv sync --frozen || uv sync

# 소스 및 스크립트 복사
COPY . /app
RUN chmod +x /app/scripts/run.sh

# 기본 포트
EXPOSE 8000

# 기본 실행명령은 docker-compose에서 command로 정의
