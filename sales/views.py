from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets

from carts.models import Cart
from sales.models import Sale, Item
from sales.serializers import SaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by('-created')
    serializer_class = SaleSerializer
    search_fields = ['sale_number', 'customer__name']

    def get_serializer_context(self):
        """
        Kita perlu menambahkan context request
        untuk keperluan validasi
        """
        context = super(SaleViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    @transaction.atomic
    def perform_create(self, serializer):
        sale = serializer.save(user=self.request.user)
        carts = Cart.objects.filter(user=self.request.user)
        item_set = []
        for cart in carts:
            item_set.append(
                Item(
                    product=cart.product,
                    sale=sale,
                    name=cart.name,
                    unit=cart.unit,
                    price=cart.price,
                    stock=cart.stock,
                    quantity=cart.quantity,
                    subtotal=cart.subtotal
                )
            )

        Item.objects.bulk_create(item_set)
        carts.delete()
