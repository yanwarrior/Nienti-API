from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .serializers import SigninSerializer, ProfileSerializer


class AccountViewSet(viewsets.ViewSet):
    # permission_classes = [AllowAny]
    #
    # @action(methods=['POST'], detail=False)
    # def signin(self, request):
    #     serializer = SigninSerializer(data=request.data)
    #
    #     if serializer.is_valid():
    #         return Response(serializer.get_json(), status=status.HTTP_200_OK)
    #
    #     return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated, IsAdminUser])
    def profile(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
