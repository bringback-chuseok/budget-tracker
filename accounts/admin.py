from django.contrib import admin

from .models import GoogleAccount, KakaoAccount, LocalAccount


@admin.register(LocalAccount)
class LocalAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "username", "updated_at")
    search_fields = ("email", "username")


@admin.register(GoogleAccount)
class GoogleAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "google_user_id", "email", "updated_at")
    search_fields = ("google_user_id", "email")


@admin.register(KakaoAccount)
class KakaoAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "kakao_user_id", "email", "updated_at")
    search_fields = ("kakao_user_id", "email")
