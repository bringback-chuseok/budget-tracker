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

## 자동 테스트

```bash
python3 manage.py test accounts
```

- 회원가입, 일반 로그인, 토큰 재발급, 로그아웃, 소셜 로그인 흐름을 Mock 기반으로 검증함  
- 최신 실행 결과: `7 tests OK`
