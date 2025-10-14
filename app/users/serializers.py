from rest_framework import serializers
from .models import Users  # 모델 예시

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'email', 'nickname']