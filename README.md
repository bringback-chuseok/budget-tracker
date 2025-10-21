# 💰 Budget Tracker

개인 가계부 시스템을 구현할 수 있습니다.
이 프로젝트는 Python 3.12 / Django 기반으로 작성되었으며,
`uv` 패키지 매니저와 `pre-commit` 훅을 사용하여 개발 환경을 관리합니다.

---

## 🚀 프로젝트 개요

Budget Tracker는 사용자가 자신의 **수입과 지출을 기록, 조회, 관리**할 수 있는 웹 애플리케이션입니다.
Django 기반의 백엔드로 안정적인 CRUD 및 인증 기능을 제공합니다.

---

## 💫 주요 기능

- **회원가입 / 로그인 / 로그아웃**
- **Django Admin Page** (관리자용)
- **계좌 CRD**
- **거래내역 CRUD**
- **거래내역 필터링**
- **개발 프로세스**: Commit → PR → Review → Merge

---

## 🧰 기술 스택

| 구분 | 사용 기술 |
|------|------------|
| **언어** | Python 3.12 |
| **패키지 매니저** | [uv](https://github.com/astral-sh/uv) |
| **프레임워크** | Django |
| **데이터베이스** | PostgreSQL |
| **컨테이너** | Docker (예시: `Dockerfile`, `docker-compose.yml` 기반) |
| **코드 품질 관리** | pre-commit, Ruff, Black, isort, autoflake |

---

## 🐍 개발 환경 설정

### 1️⃣ uv 기반 Python 환경 설정
```bash
# uv 설치 (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 패키지 설치
uv venv
uv sync

### 1️⃣ uv 기반 Python 환경 설정


# uv 설치 (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 패키지 설치
uv venv
uv sync
```

> Python 3.12 이상 환경을 권장합니다.

---

### 1️⃣ 설치 및 등록


# 개발 의존성으로 pre-commit 추가
uv add --dev pre-commit

# pre-commit 훅 등록 (프로젝트 루트에서 실행)
pre-commit install

> 위 명령은 `.git/hooks/pre-commit`에 훅 스크립트를 설치합니다.
> 한 번만 실행하면 이후 모든 커밋 시 자동으로 코드 검사/포맷이 수행됩니다.

---

### 2️⃣ 수동 실행 (전체 파일 검사)

pre-commit run --all-files

> 코드 전체를 강제로 검사/자동 수정할 때 사용합니다.

---

### 3️⃣ pre-commit에서 수행되는 작업

| 도구 | 역할 |
|------|------|
| **Ruff** | 린트 검사 및 자동 수정 |
| **Black** | 코드 포매팅 |
| **isort** | import 정렬 |
| **autoflake** | 불필요한 import/변수 제거 |
| **pre-commit-hooks** | 기본 위생 검사 (공백, EOF, YAML 등) |

---

### 4️⃣ 협업 안내

- 저장소를 클론한 후 반드시 한 번 다음 명령을 실행해야 합니다:
  pre-commit install
- 이후에는 커밋 시 자동으로 pre-commit 훅이 동작합니다.
- 만약 수동으로 실행하고 싶다면:
  pre-commit run --all-files

> `pre-commit`은 **로컬 Git 훅 기반**으로 동작하므로,
> 설정 파일(`.pre-commit-config.yaml`)만 커밋되어도 **자동으로 동작하지 않습니다.**
> 각 개발자가 직접 훅을 설치해야 합니다.

---

## 🐳 Docker

📦 이미지 빌드 및 DockerHub 푸시

```bash
# 로컬에서 Docker 이미지 빌드
docker build -t budget-tracker .

# DockerHub에 푸시할 태그 지정
docker tag budget-tracker dockeruserid/budget-tracker:latest

# DockerHub 로그인 후 푸시
docker login
docker push dockeruserid/budget-tracker:latest
```
☁️ AWS EC2에서 실행

```bash
# Docker 설치 (Ubuntu 기준)
sudo apt update
sudo apt install docker.io -y

# DockerHub에서 이미지 pull
docker pull dockeruserid/budget-tracker:latest

# 컨테이너 실행
docker run -d -p 80:8000 --name budget-tracker dockeruserid/budget-tracker:latest
```
EC2 보안 그룹에서 포트 80이 열려 있어야 외부 접속이 가능합니다.

📄 docker-compose.yml (요약)
```yaml
version: '3.9'
services:
  db:
    image: postgres:15-alpine
    env_file: [.env]
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ..."]
  web:
    build: .
    command: /app/scripts/run.sh
    ports: ["8000:8000"]
    depends_on:
      db:
        condition: service_healthy
    volumes: [.:/app, staticfiles:/app/staticfiles]
volumes:
  postgres_data:
  staticfiles:
```
전체 코드는 docker-compose.yml 파일을 참고하세요.

🧼 .dockerignore 설정
이미지 빌드 시 불필요하거나 민감한 파일이 포함되지 않도록 .dockerignore를 설정했습니다:
```dockerignore
.venv/
__pycache__/
*.pyc

.git
.gitignore
.env

docker-compose.yml
```
.env, .git, .venv 등은 이미지에 포함되지 않으며, 안전하게 배포할 수 있습니다.

---

## 🧪 실행 (로컬 환경)

# Django 실행
python manage.py runserver

---

## 🤝 협업 규칙

1. **pre-commit 설치 필수**
   pre-commit install

2. **커밋 → PR → 리뷰 → 머지 순서**로 진행
3. 포맷팅 오류 발생 시 pre-commit이 자동 수정하므로,
   수정된 파일은 다시 `git add` 후 커밋합니다.

---
