from django.db import models
from app.accounts.models import Accounts
# Create your models here.
class Histories(models.Model):
    account_id = models.ForeignKey(
        Accounts,
        on_delete=models.CASCADE,
        null=False,
        related_name='histories_records'
    )
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    balance = models.DecimalField(decimal_places=2, max_digits=20)
    desc = models.TextField()
    inout_type = models.CharField(max_length=20)
    transact_type = models.CharField(max_length=20)
    transacted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} - {self.desc}"

    class Meta:
        verbose_name = '거래'
        verbose_name_plural = '거래 내역'