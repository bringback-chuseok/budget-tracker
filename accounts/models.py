from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LocalAccount(TimeStampedModel):
    """자체 회원가입 계정 정보를 저장한다."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="local_account",
    )
    email = models.EmailField()
    username = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "로컬 계정"
        verbose_name_plural = "로컬 계정"

    def __str__(self) -> str:  # pragma: no cover - admin 표시용
        return f"{self.username} ({self.email})"


class GoogleAccount(TimeStampedModel):
    """구글 소셜 로그인 계정 정보를 저장한다."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="google_account",
    )
    google_user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    name = models.CharField(max_length=150, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    profile = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "구글 계정"
        verbose_name_plural = "구글 계정"

    def __str__(self) -> str:  # pragma: no cover - admin 표시용
        return f"{self.google_user_id} ({self.email})"


class KakaoAccount(TimeStampedModel):
    """카카오 소셜 로그인 계정 정보를 저장한다."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kakao_account",
    )
    kakao_user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    nickname = models.CharField(max_length=150, blank=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    profile = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "카카오 계정"
        verbose_name_plural = "카카오 계정"

    def __str__(self) -> str:  # pragma: no cover - admin 표시용
        return f"{self.kakao_user_id} ({self.email})"
