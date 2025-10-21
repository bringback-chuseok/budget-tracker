from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import LocalAccount

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            User.USERNAME_FIELD,
            "email",
            "password",
        )
        extra_kwargs = {
            User.USERNAME_FIELD: {"required": True},
            "email": {"required": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        LocalAccount.objects.create(
            user=user,
            email=user.email,
            username=getattr(user, user.USERNAME_FIELD),
        )
        return user


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=("google", "kakao"))
    token = serializers.CharField()


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    기본 TokenObtainPairSerializer를 확장하여 커스텀 클레임과 검증 로직을 추가한다.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            raise serializers.ValidationError("비활성화된 사용자입니다.")

        data.update({"detail": "로그인에 성공했습니다."})
        return data
