from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

User = get_user_model()


class UserListCreateView(APIView):
    def get(self, request):
        qs = User.objects.all().order_by("-id")
        return Response(UserSerializer(qs, many=True).data)

    def post(self, request):
        # username, email, password, nickname, phone_number 등을 입력받을 수 있음
        data = request.data.copy()
        password = data.pop("password", None)

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = User(**serializer.validated_data)
        if password:
            user.set_password(password)
        user.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
