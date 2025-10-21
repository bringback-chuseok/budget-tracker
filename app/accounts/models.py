from django.conf import settings
from django.db import models
from django.utils import timezone  # noqa: F401

from app.constants import ACCOUNT_TYPE, BANK_CODES  # constants.py에서 import


class Accounts(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← 스와퍼블 참조
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    account_name = models.CharField(max_length=50)  # 계좌 별명
    account_password = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_code = models.CharField(
        max_length=3,
        choices=BANK_CODES,
        default="000",  # 기본값
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE,
        default="CHECKING",  # 기본값 입출금
    )
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name} ({self.get_account_type_display()})"

    class Meta:
        verbose_name = "계좌"
        verbose_name_plural = "계좌 목록"
