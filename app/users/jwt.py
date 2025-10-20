from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    로그인 성공 시 access/refresh 토큰을 HttpOnly 쿠키로 저장.
    """

    def post(self, request, *args, **kwargs):
        resp = super().post(
            request, *args, **kwargs
        )  # resp.data: {'access':..., 'refresh':...}
        access = resp.data.get("access")
        refresh = resp.data.get("refresh")

        # 운영에서는 secure=True가 안전합니다. DEBUG일 땐 False로 둡니다.
        secure = not settings.DEBUG

        if access:
            resp.set_cookie(
                "access",
                access,
                httponly=True,
                secure=secure,
                samesite="Lax",
                max_age=int(getattr(settings, "JWT_ACCESS_MINUTES", 15)) * 60,
            )
        if refresh:
            resp.set_cookie(
                "refresh",
                refresh,
                httponly=True,
                secure=secure,
                samesite="Lax",
                max_age=int(getattr(settings, "JWT_REFRESH_DAYS", 7)) * 24 * 60 * 60,
            )

        # 바디에 토큰을 남기고 싶지 않다면 다음 줄 주석 해제
        # resp.data = {"detail": "ok"}

        return resp
