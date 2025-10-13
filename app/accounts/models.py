from django.db import models
from app.users.models import Users
# Create your models here.
class Accounts(models.Model):
    user_id = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        null=False,
        related_name="accounts"
    )
    account_name = models.CharField(max_length=50) # 계좌 별명
    account_password = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank_code = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20)
    balance = models.DecimalField(decimal_places=2, max_digits=20)

    def __str__(self):
        return f"{self.account_name} - {self.account_type}"

    class Meta:
        verbose_name = '계좌'
        verbose_name_plural = '계좌 목록'