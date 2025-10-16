from django.contrib import admin

from .models import Users

# Register your models here.


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "nickname",
        "name",
        "phone_number",
        "is_admin",
        "is_staff",
        "is_active",
        "last_login",
    )

    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "nickname", "phone_number")
    readonly_fields = ("is_admin", "created_at", "updated_at", "last_login")
    ordering = ("-created_at",)
