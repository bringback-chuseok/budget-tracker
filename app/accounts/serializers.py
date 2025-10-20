from rest_framework import serializers

from .models import Accounts

# JSON변환 및 TYPE검증을 위해 DRF사용


class AccountSerializer(serializers.ModelSerializer):
    initial_balance = serializers.DecimalField(
        max_digits=20, decimal_places=2, write_only=True
    )

    class Meta:
        model = Accounts
        fields = [
            "id",
            "account_number",
            "bank_code",
            "account_type",
            "balance",
            "account_name",
            "account_password",
            "initial_balance",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "balance", "is_deleted", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["balance"] = validated_data.pop("initial_balance")
        return super().create(validated_data)

    # 사용자의 입력값을 initial_balance에 담아 serializer가 balance에 반영
    # 핵심 기능인 잔액관리는 serializer에서 한번에 처리하는게 유지보수보안에 유리
