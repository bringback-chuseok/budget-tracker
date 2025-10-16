from django.db import models
from django.utils import timezone  # noqa: F401

from app.users.models import Users


# Create your models here.
class Accounts(models.Model):
    #계좌타입. 저축.입출금.업무.투자.대출.
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings'),
        ('CHECKING', 'Checking'),
        ('BUSINESS', 'Business'),
        ('INVESTMENT', 'Investment'),
        ('LOAN', 'Loan'),
    ]

    user_id = models.ForeignKey(
        Users, on_delete=models.CASCADE, null=False, related_name="accounts"
    )
    account_name = models.CharField(max_length=50)  # 계좌 별명
    account_password = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank_code = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20)
    balance = models.DecimalField(decimal_places=2, max_digits=20)
    #+삭제,생성,수정
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name} - {self.account_type}"

    class Meta:
        verbose_name = "계좌"
        verbose_name_plural = "계좌 목록"
