from django.contrib import admin

from .models import Users

# Register your models here.


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "nickname",
        "first_name",
        "phone_number",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name", "nickname", "phone_number")
    # AbstractUser 기반 필드셋 구성
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "개인정보",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "nickname",
                    "phone_number",
                )
            },
        ),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("중요 날짜", {"fields": ("last_login", "date_joined")}),
    )

    # admin에서 사용자 추가 화면 구성
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    ordering = ("-id",)
