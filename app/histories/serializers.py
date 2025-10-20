from django.db import transaction
from rest_framework import serializers

from app.accounts.models import Accounts  # Accounts 모델 경로 확인

from .models import Histories


class HistorySerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Accounts.objects.all(), source="account"
    )

    class Meta:
        model = Histories
        fields = ["id", "account_id", "amount", "inout_type", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        account = validated_data.pop("account_id")
        amount = validated_data["amount"]
        inout_type = validated_data["inout_type"].lower()

        if amount <= 0:
            raise serializers.ValidationError("금액은 0보다 커야 합니다.")

        with transaction.atomic():
            # 계좌 잠금
            account = Accounts.objects.select_for_update().get(pk=account.pk)

            # 자동 합산
            if inout_type == "in":
                new_balance = account.balance + amount
            elif inout_type == "out":
                if account.balance < amount:  # 잔액 부족
                    raise serializers.ValidationError("잔액이 부족합니다.")
                new_balance = account.balance - amount
            else:  # 입출금 유효성
                raise serializers.ValidationError(
                    "inout_type은 'in' 또는 'out'만 가능합니다."
                )

            # 계좌 업데이트
            account.balance = new_balance
            account.save()

            validated_data["account"] = account

            return super().create(validated_data)
