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

## 🐳 Docker (예시)

> ⚠️ 실제 Docker 환경은 별도 동렬님께서 구성 중입니다.
> 아래 내용은 예시이며, 변경될 수 있습니다.

# docker-compose.yml (예시)
version: "3.9"

services:
  web:
    build: .
    container_name: budget-tracker-web
    command: uvicorn config.asgi:application --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: postgres:15
    container_name: budget-tracker-db
    restart: always
    environment:
      POSTGRES_USER: budget
      POSTGRES_PASSWORD: tracker
      POSTGRES_DB: budget_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data/

volumes:
  postgres_data:

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

# Auth Feature Summary

## Manual Verification

- **Google Social Login**
  1. `python3 manage.py migrate && python3 manage.py runserver`
  2. Google OAuth Playground에서 `id_token` 발급
  3. Postman Desktop Agent로 `POST http://127.0.0.1:8000/auth/login/social/` 호출
     ```json
     {
       "provider": "google",
       "token": "<발급받은 id_token>"
     }
     ```
  4. 응답: `200 OK`, `access_token` / `refresh_token` 쿠키 정상 발급 확인

- **Kakao Social Login**
  - Access Token 발급 및 이메일 동의 항목 설정이 추가로 필요하여 현재 검증 보류 상태

### 데이터 저장 구조

- 자체 회원 가입 정보: `LocalAccount`
- 구글 로그인 정보: `GoogleAccount`
- 카카오 로그인 정보: `KakaoAccount`
- 모든 계정은 Django 기본 User와 연결되어 JWT 발급 및 권한 처리를 공유합니다.

## 자동 테스트

```bash
python3 manage.py test accounts
```

- 회원가입, 일반 로그인, 토큰 재발급, 로그아웃, 소셜 로그인 흐름을 Mock 기반으로 검증함
- 최신 실행 결과: `7 tests OK`
