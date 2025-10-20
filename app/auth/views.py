from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone as dj_timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.users.models import Users

from .models import AuthToken
from .serializers import LoginSerializer, RefreshSerializer, SignupSerializer


def _jwt_times():
    access_minutes = int(getattr(settings, "JWT_ACCESS_MINUTES", 15))
    refresh_days = int(getattr(settings, "JWT_REFRESH_DAYS", 7))
    return access_minutes, refresh_days


def _generate_tokens(user: Users):
    access_minutes, refresh_days = _jwt_times()
    now = dj_timezone.now()

    payload_access = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=access_minutes)).timestamp()),
    }
    payload_refresh = {
        "sub": str(user.id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=refresh_days)).timestamp()),
    }

    access = jwt.encode(payload_access, settings.SECRET_KEY, algorithm="HS256")
    refresh = jwt.encode(payload_refresh, settings.SECRET_KEY, algorithm="HS256")

    # 저장 (토큰 관리)
    AuthToken.objects.create(
        user=user,
        token=access,
        token_type="access",
        expires_at=now + timedelta(minutes=access_minutes),
    )
    AuthToken.objects.create(
        user=user,
        token=refresh,
        token_type="refresh",
        expires_at=now + timedelta(days=refresh_days),
    )

    return access, refresh, payload_access["exp"], payload_refresh["exp"]


def _verify_password(user: Users, raw_password: str) -> bool:
    # NOTE: 현재 Users.password가 해시 저장이 아니라 평문으로 가정 (필드 제한 때문).
    return user.password == raw_password


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        access, refresh, access_exp, refresh_exp = _generate_tokens(user)
        return Response(
            {
                "user_id": user.id,
                "email": user.email,
                "access": access,
                "refresh": refresh,
                "access_expires": access_exp,
                "refresh_expires": refresh_exp,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            return Response(
                {"detail": "잘못된 자격 증명입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _verify_password(user, password):
            return Response(
                {"detail": "잘못된 자격 증명입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.last_login = dj_timezone.now()
        user.save(update_fields=["last_login"])

        # 기존 refresh 토큰을 모두 revoke(선택)
        AuthToken.objects.filter(user=user, token_type="refresh", revoked=False).update(
            revoked=True
        )

        access, refresh, access_exp, refresh_exp = _generate_tokens(user)
        return Response(
            {
                "user_id": user.id,
                "email": user.email,
                "access": access,
                "refresh": refresh,
                "access_expires": access_exp,
                "refresh_expires": refresh_exp,
            }
        )


class RefreshView(APIView):
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["refresh"]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "리프래시 토큰 만료"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "유효하지 않은 토큰"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if payload.get("type") != "refresh":
            return Response(
                {"detail": "리프래시 토큰이 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 토큰 저장 레코드 검증
        try:
            record = AuthToken.objects.get(token=token, token_type="refresh")
        except AuthToken.DoesNotExist:
            return Response(
                {"detail": "저장된 토큰이 아닙니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if record.revoked:
            return Response(
                {"detail": "토큰이 폐기되었습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if record.expires_at < dj_timezone.now():
            return Response(
                {"detail": "리프래시 토큰 만료"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # 액세스 토큰만 재발급 (리프래시는 유지). 필요시 회전 구현 가능.
        user = record.user
        access_minutes, _ = _jwt_times()
        now = dj_timezone.now()
        payload_access = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=access_minutes)).timestamp()),
        }
        access = jwt.encode(payload_access, settings.SECRET_KEY, algorithm="HS256")
        AuthToken.objects.create(
            user=user,
            token=access,
            token_type="access",
            expires_at=now + timedelta(minutes=access_minutes),
        )

        return Response({"access": access, "access_expires": payload_access["exp"]})
