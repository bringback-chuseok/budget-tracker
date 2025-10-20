from rest_framework import serializers

from app.users.models import Users


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=50)
    nickname = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )

    def validate_email(self, value):
        if Users.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value

    def create(self, validated_data):
        # NOTE: 현재 단계에서는 Users.password 필드 길이 제한(50) 때문에 해시 미적용.
        # 보안 단계에서 Django 해시 적용 및 마이그레이션 필요.
        return Users.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
