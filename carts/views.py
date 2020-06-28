from rest_framework import viewsets

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
