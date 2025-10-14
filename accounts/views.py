from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import CookieTokenObtainPairSerializer, RegisterSerializer


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

        access = response.data.get('access')
        refresh = response.data.get('refresh')

        if access:
            _set_cookie(response, settings.AUTH_COOKIE, access, settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
        if refresh:
            _set_cookie(response, settings.AUTH_COOKIE_REFRESH, refresh, settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])

        detail = response.data.get('detail', '로그인에 성공했습니다.')
        response.data = {'detail': detail}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh') or request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if refresh_token is None:
            return Response({'detail': '리프레시 토큰이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({'detail': '유효하지 않은 토큰입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        access = serializer.validated_data.get('access')
        new_refresh = serializer.validated_data.get('refresh')

        response = Response({'detail': '토큰을 재발급했습니다.'}, status=status.HTTP_200_OK)

        if access:
            _set_cookie(response, settings.AUTH_COOKIE, access, settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
        if new_refresh:
            _set_cookie(response, settings.AUTH_COOKIE_REFRESH, new_refresh, settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])

        return response


class CookieTokenBlacklistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if refresh_token is None:
            return Response({'detail': '리프레시 토큰이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': '유효하지 않은 리프레시 토큰입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({'detail': '로그아웃되었습니다.'}, status=status.HTTP_200_OK)
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
                'detail': '회원가입이 완료되었습니다.',
                'user': {
                    'id': user.pk,
                    'username': getattr(user, user.USERNAME_FIELD),
                    'email': user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )
