from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):
    # AbstractUser 기본 필드:
    # username, password(해시), email, first_name, last_name, is_staff, is_active, is_superuser, last_login, date_joined ...
    nickname = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.email})"

    class Meta:
        verbose_name = "유저"
        verbose_name_plural = "유저 목록"
