from rest_framework import generics, permissions
from .models import Account
from .serializers import AccountSerializer

class AccountCreateView(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
