from django.contrib import admin
from django.urls import include, path

# # prefix 없는 ver
# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("users/", include("app.users.urls")),
#     path("accounts/", include("app.accounts.urls")),
#     path("histories/", include("app.histories.urls")),
# ]

# prefix 추가 ver
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("app.users.urls")),
    path("api/histories/", include("app.histories.urls")),
    path("api/accounts/", include("app.accounts.urls")),
]
