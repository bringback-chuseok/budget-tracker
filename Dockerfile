# 베이스 이미지
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 필수 패키지 설치 (uv 실행 및 빌드 도구 등)
RUN apt-get update && apt-get install -y curl build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# pyproject.toml & uv.lock 복사 및 설치
COPY . /scripts /scripts
RUN chmod +x /scripts/run.sh

# 애플리케이션 코드 복사
COPY . /app

# 포트 설정 (FastAPI일 경우도 동일)
EXPOSE 8000

# Django 개발 서버 실행
CMD ["/scripts/run.sh"]
