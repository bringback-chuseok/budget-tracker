from rest_framework import generics, permissions
from .models import Accounts
from .serializers import AccountSerializer

#계좌생성
class AccountCreateView(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

#계좌조회
class AccountListView(generics.ListAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Accounts.objects.filter(user=self.request.user, is_deleted=False)

#계좌수정
class AccountUpdateView(generics.UpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Accounts.objects.filter(user=self.request.user, is_deleted=False)

#계좌삭제 : 불리언으로 소프트삭제
class AccountDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Accounts.objects.filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
