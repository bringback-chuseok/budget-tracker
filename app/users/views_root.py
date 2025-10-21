from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import AccessToken


def root_redirect(request):
    token = request.COOKIES.get("access")
    if not token:
        return redirect("/login")  # 로그인 페이지로

    try:
        AccessToken(token)  # 유효성/만료 검사 (서명 불일치, 만료 시 예외)
    except Exception:
        return redirect("/login")

    # 로그인되어 있으면 원하는 곳으로
    return redirect("/api/users/")  # 임시
