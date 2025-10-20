from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# # prefix 없는 ver
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("users/", include("app.users.urls")),
#     path("users/", include("app.users.urls")),
#     path("histories/", include("app.histories.urls")),
# ]

# prefix 추가 ver
urlpatterns = [
    path("admin/", admin.site.urls),
    # Page routes
    path(
        "users/signup/",
        TemplateView.as_view(template_name="users/signup.html"),
        name="page-signup",
    ),
    # API routes
    path("api/users/", include("app.users.urls")),
    path("api/histories/", include("app.histories.urls")),
    path("api/accounts/", include("app.accounts.urls")),
    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
