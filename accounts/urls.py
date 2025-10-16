from django.urls import path

from .views import (
    CookieTokenBlacklistView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    RegisterView,
    SocialLoginView,
)

app_name = "accounts"


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("login/social/", SocialLoginView.as_view(), name="social_login"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", CookieTokenBlacklistView.as_view(), name="logout"),
]
