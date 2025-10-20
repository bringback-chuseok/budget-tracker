from django.db import models

from app.users.models import Users


class AuthToken(models.Model):
    TOKEN_TYPE_CHOICES = (
        ("access", "Access"),
        ("refresh", "Refresh"),
    )

    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="auth_tokens"
    )
    token = models.CharField(max_length=512, unique=True)
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "token_type"]),
            models.Index(fields=["expires_at"]),
        ]
        verbose_name = "인증 토큰"
        verbose_name_plural = "인증 토큰 목록"

    def __str__(self):
        return f"{self.user_id}:{self.token_type}:{'revoked' if self.revoked else 'active'}"
