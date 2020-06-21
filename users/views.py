from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import ProfileSerializer


class UserViewSet(viewsets.ViewSet):

    @action(methods=['GET'], detail=False)
    def profile(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
