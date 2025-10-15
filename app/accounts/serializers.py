from rest_framework import serializers
from .models import Accounts

class AccountSerializer(serializers.ModelSerializer):
    initial_balance = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True)

    class Meta:
        model = Accounts
        fields = ['id', 'name', 'currency', 'account_type', 'metadata', 'current_balance', 'initial_balance', 'created_at']
        read_only_fields = ['id', 'current_balance', 'created_at']

    def create(self, validated_data):
        validated_data['current_balance'] = validated_data.pop('initial_balance')
        return super().create(validated_data)
