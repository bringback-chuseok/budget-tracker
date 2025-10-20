from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import GoogleAccount, KakaoAccount
from .serializers import (
    CookieTokenObtainPairSerializer,
    RegisterSerializer,
    SocialLoginSerializer,
)
from .social import SocialLoginError, get_social_profile

User = get_user_model()


def _set_cookie(response, name, value, lifetime):
    response.set_cookie(
        name,
        value,
        max_age=int(lifetime.total_seconds()),
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
    )


def _clear_auth_cookies(response):
    response.delete_cookie(
        settings.AUTH_COOKIE,
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        settings.AUTH_COOKIE_REFRESH,
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CookieTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        access = response.data.get("access")
        refresh = response.data.get("refresh")

        if access:
            _set_cookie(
                response,
                settings.AUTH_COOKIE,
                access,
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            )
        if refresh:
            _set_cookie(
                response,
                settings.AUTH_COOKIE_REFRESH,
                refresh,
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            )

        detail = response.data.get("detail", "로그인에 성공했습니다.")
        response.data = {"detail": detail}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(
            settings.AUTH_COOKIE_REFRESH
        )
        if refresh_token is None:
            return Response(
                {"detail": "리프레시 토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access = serializer.validated_data.get("access")
        new_refresh = serializer.validated_data.get("refresh")

        response = Response(
            {"detail": "토큰을 재발급했습니다."}, status=status.HTTP_200_OK
        )

        if access:
            _set_cookie(
                response,
                settings.AUTH_COOKIE,
                access,
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            )
        if new_refresh:
            _set_cookie(
                response,
                settings.AUTH_COOKIE_REFRESH,
                new_refresh,
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            )

        return response


class CookieTokenBlacklistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if refresh_token is None:
            return Response(
                {"detail": "리프레시 토큰이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "유효하지 않은 리프레시 토큰입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {"detail": "로그아웃되었습니다."}, status=status.HTTP_200_OK
        )
        _clear_auth_cookies(response)
        return response


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "detail": "회원가입이 완료되었습니다.",
                "user": {
                    "id": user.pk,
                    "username": getattr(user, user.USERNAME_FIELD),
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class SocialLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SocialLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        token = serializer.validated_data["token"]

        try:
            profile = get_social_profile(provider, token)
        except SocialLoginError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, created = self._get_or_create_user(profile, token)
        except SocialLoginError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                "detail": "소셜 로그인에 성공했습니다.",
                "is_new_user": created,
            },
            status=status.HTTP_200_OK,
        )
        _set_cookie(
            response,
            settings.AUTH_COOKIE,
            str(refresh.access_token),
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        )
        _set_cookie(
            response,
            settings.AUTH_COOKIE_REFRESH,
            str(refresh),
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        )
        return response

    @transaction.atomic
    def _get_or_create_user(self, profile, raw_token):
        if profile.provider == "google":
            return self._get_or_create_google_user(profile, raw_token)
        if profile.provider == "kakao":
            return self._get_or_create_kakao_user(profile, raw_token)
        raise SocialLoginError("지원하지 않는 소셜 로그인 제공자입니다.")

    def _get_or_create_google_user(self, profile, raw_token):
        try:
            account = GoogleAccount.objects.select_related("user").get(
                google_user_id=profile.provider_user_id
            )
            user = account.user
            created = False
        except GoogleAccount.DoesNotExist:
            user = self._create_social_user(profile)
            account = GoogleAccount(
                user=user,
                google_user_id=profile.provider_user_id,
            )
            created = True

        account.email = profile.email or account.email
        account.name = profile.name or account.name
        account.access_token = raw_token
        account.save()
        return user, created

    def _get_or_create_kakao_user(self, profile, raw_token):
        try:
            account = KakaoAccount.objects.select_related("user").get(
                kakao_user_id=profile.provider_user_id
            )
            user = account.user
            created = False
        except KakaoAccount.DoesNotExist:
            user = self._create_social_user(profile)
            account = KakaoAccount(
                user=user,
                kakao_user_id=profile.provider_user_id,
            )
            created = True

        account.email = profile.email or account.email
        account.nickname = profile.name or account.nickname
        account.access_token = raw_token
        account.save()
        return user, created

    def _create_social_user(self, profile):
        base_username = (
            profile.email.split("@")[0] if profile.email else profile.provider_user_id
        )
        candidate = base_username
        suffix = 1
        while User.objects.filter(username=candidate).exists():
            candidate = f"{base_username}_{suffix}"
            suffix += 1

        user = User.objects.create_user(
            username=candidate,
            email=profile.email or "",
            password=None,
        )
        if profile.name and hasattr(user, "first_name"):
            user.first_name = profile.name
            user.save(update_fields=["first_name"])
        return user
