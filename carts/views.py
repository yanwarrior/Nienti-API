from rest_framework import viewsets

from carts.models import Cart
from carts.serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().order_by('-created')
    serializer_class = CartSerializer
