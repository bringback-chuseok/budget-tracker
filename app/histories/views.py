from rest_framework import generics, permissions

from .models import Histories
from .serializers import HistorySerializer


# 거래 생성
class HistoryCreateView(generics.CreateAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


# 거래 조회
class HistoryListView(generics.ListAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Histories.objects.filter(account_id__user=self.request.user)


# 상세 조회
class HistoryDetailView(generics.RetrieveAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Histories.objects.filter(account_id__user=self.request.user)


# 거래 수정
class HistoryUpdateView(generics.UpdateAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Histories.objects.filter(account_id__user=self.request.user)


# 거래 삭제
class HistoryDeleteView(generics.DestroyAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Histories.objects.filter(account_id__user=self.request.user)
