from django.contrib import admin

from .models import Accounts


@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "account_name",
        "account_number",
        "bank_code",
        "account_type",
        "balance",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("account_type", "is_deleted", "bank_code")
    search_fields = ("account_name", "account_number", "user_id__username")
    readonly_fields = ("created_at", "updated_at")
