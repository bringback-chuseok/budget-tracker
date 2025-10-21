from django.contrib import admin

from .models import Histories


@admin.register(Histories)
class HistoriesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_id",
        "amount",
        "balance",
        "inout_type",
        "transact_type",
        "transacted_at",
    )
    list_filter = ("inout_type", "transact_type", "transacted_at")
    search_fields = ("desc", "account__username")  # Accounts 모델 필드에 맞게 수정 필요
    readonly_fields = ("balance", "transacted_at")
