import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

KAKAO_ME_URL = getattr(settings, "KAKAO_ME_URL", "https://kapi.kakao.com/v2/user/me")
KAKAO_TOKEN_INFO_URL = getattr(
    settings, "KAKAO_TOKEN_INFO_URL", "https://kapi.kakao.com/v1/user/access_token_info"
)
KAKAO_TOKEN_URL = getattr(
    settings, "KAKAO_TOKEN_URL", "https://kauth.kakao.com/oauth/token"
)


def _upsert_user_and_issue_jwt(access_token: str):
    """카카오 access_token으로 사용자 조회/생성 후 JWT 반환"""
    headers = {"Authorization": f"Bearer {access_token}"}

    # (선택) 토큰 검증
    info_res = requests.get(KAKAO_TOKEN_INFO_URL, headers=headers, timeout=5)
    if info_res.status_code != 200:
        return None, Response(
            {"detail": "Invalid Kakao access token"}, status=status.HTTP_400_BAD_REQUEST
        )

    # 사용자 정보
    me_res = requests.get(KAKAO_ME_URL, headers=headers, timeout=5)
    if me_res.status_code != 200:
        return None, Response(
            {"detail": "Failed to fetch Kakao user"}, status=status.HTTP_400_BAD_REQUEST
        )
    me = me_res.json()

    kakao_id = me.get("id")
    if not kakao_id:
        return None, Response(
            {"detail": "Kakao user id not found"}, status=status.HTTP_400_BAD_REQUEST
        )

    kakao_account = me.get("kakao_account", {}) or {}
    profile = kakao_account.get("profile", {}) or {}
    nickname = profile.get("nickname") or ""

    # 이메일 동의 범위를 받지 않은 경우 대비 (모델 email unique=True)
    email = kakao_account.get("email")
    username = f"kakao_{kakao_id}"
    if not email:
        email = f"{username}@kakao.local"  # synth email (unique 보장)

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "nickname": nickname[:20] if hasattr(User, "nickname") else "",
            "first_name": "",
        },
    )

    # 최초 생성 후 이메일이 비어있었다가 추후 동의받은 경우 등
    if not user.email and email:
        user.email = email

    if nickname and hasattr(user, "nickname"):
        user.nickname = nickname[:20]

    if not user.has_usable_password():
        user.set_unusable_password()
    user.save()

    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    return (str(refresh), access), None


class SocialKakaoCallbackView(APIView):
    """
    Kakao Auth Code Redirect 콜백 엔드포인트
    1) 쿼리로 받은 code로 카카오 토큰 교환
    2) access_token으로 유저 upsert + JWT 발급
    3) JWT를 쿠키로 설정 후 원하는 페이지로 리다이렉트
    """

    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        error = request.query_params.get("error")
        if error:
            return Response(
                {"detail": f"kakao error: {error}"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not code:
            return Response(
                {"detail": "code is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 토큰 교환
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        }
        try:
            token_res = requests.post(KAKAO_TOKEN_URL, data=data, timeout=5)
        except requests.RequestException:
            return Response(
                {"detail": "Kakao token exchange failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if token_res.status_code != 200:
            return Response(
                {"detail": "Invalid authorization code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_json = token_res.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return Response(
                {"detail": "No access_token in Kakao response"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        jwt_pair, err_resp = _upsert_user_and_issue_jwt(access_token)
        if err_resp:
            return err_resp

        refresh, access = jwt_pair

        # 쿠키 설정
        secure = not getattr(settings, "DEBUG", False)
        access_max_age = int(getattr(settings, "JWT_ACCESS_MINUTES", 15)) * 60
        refresh_max_age = int(getattr(settings, "JWT_REFRESH_DAYS", 7)) * 24 * 60 * 60

        # 최종 이동 목적지 (없으면 홈/히스토리 등)
        redirect_to = request.GET.get("next") or "/api/histories"

        resp = redirect(redirect_to)
        resp.set_cookie(
            "access",
            access,
            httponly=True,
            secure=secure,
            samesite="Lax",
            max_age=access_max_age,
        )
        resp.set_cookie(
            "refresh",
            refresh,
            httponly=True,
            secure=secure,
            samesite="Lax",
            max_age=refresh_max_age,
        )
        return resp


class SocialKakaoLoginView(APIView):
    """
    (선택) 기존 팝업 임플리시트 플로우 호환: 프론트에서 access_token을 직접 보내는 경우
    """

    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("access_token") or request.data.get("token")
        if not access_token:
            return Response(
                {"detail": "access_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        jwt_pair, err_resp = _upsert_user_and_issue_jwt(access_token)
        if err_resp:
            return err_resp

        refresh, access = jwt_pair
        secure = not getattr(settings, "DEBUG", False)
        access_max_age = int(getattr(settings, "JWT_ACCESS_MINUTES", 15)) * 60
        refresh_max_age = int(getattr(settings, "JWT_REFRESH_DAYS", 7)) * 24 * 60 * 60

        resp = Response({"detail": "ok"}, status=status.HTTP_200_OK)
        resp.set_cookie(
            "access",
            access,
            httponly=True,
            secure=secure,
            samesite="Lax",
            max_age=access_max_age,
        )
        resp.set_cookie(
            "refresh",
            refresh,
            httponly=True,
            secure=secure,
            samesite="Lax",
            max_age=refresh_max_age,
        )
        return resp
