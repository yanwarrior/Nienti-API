from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.models import Cart
from carts.serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().order_by('-created')
    serializer_class = CartSerializer

    def get_serializer_context(self):
        """
        Kita perlu menambahkan context request
        untuk keperluan validasi cart yang
        memiliki produk yang serupa.
        """
        context = super(CartViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['DELETE'])
    def clear(self, request, pk=None):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def summary(self, request, pk=None):
        queryset = self.get_queryset()
        cart_summary = queryset.aggregate(summary=Coalesce(Sum('subtotal'), 0))
        return Response(data=cart_summary)
