from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.models import Cart
from products.models import Product
from products.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created')
    serializer_class = ProductSerializer
    search_fields = [
        'name',
        'unit',
    ]

    @action(detail=False, methods=['GET'])
    def choices(self, request, pk=None):
        """
        Method action digunakan untuk
        menampilkan daftar produk di modal multichoices
        dimana product yang memiliki cart tidak akan
        tampil. Ini tidak berimpact pada list produk
        pada method list.
        """
        product_exclude = Cart.objects.filter(user=self.request.user).values_list('product')
        queryset = self.filter_queryset(self.get_queryset()).exclude(pk__in=product_exclude)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
