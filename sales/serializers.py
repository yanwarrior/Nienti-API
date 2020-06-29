from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from carts.models import Cart
from sales.models import Sale, Item


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id',
            'customer',
            'user',
            'sale_number',
            'sale_date',
            'total',
            'total_after',
            'discount',
            'tax',
            'pay',
            'change',
        ]

        read_only_fields = ['user']

    def validate(self, attrs):
        errors = []
        request = self.context.get('request')

        carts = Cart.objects.filter(user=request.user)
        total = attrs.get('total')
        total_after = attrs.get('total_after')
        discount = attrs.get('discount')
        tax = attrs.get('tax')
        pay = attrs.get('pay')
        change = attrs.get('change')

        if not carts:
            raise ValidationError('Cart not available!')

        summary = carts.aggregate(total=Coalesce(Sum('subtotal'), 0))
        if summary.get('total') == 0:
            raise ValidationError('Invalid carts')

        if summary.get('total') != total:
            raise ValidationError('Total and summary of item not match!')

        if ((total - discount) + tax) < total_after:
            raise ValidationError('Invalid total price')

        if pay - ((total - discount) + tax) != change:
            raise ValidationError('Invalid pay and change!')

        if (pay - ((total - discount) + tax)) < 0:
            raise ValidationError('Pay enough!')

        for cart in carts:
            if cart.product.stock <= 0:
                errors.append(f'Stock product {cart.product.name} is zero!')

            if (cart.product.stock - cart.quantity) < 0:
                errors.append(f'Stock not enough in product {cart.product.name}!')

            if cart.subtotal != (cart.price * cart.quantity):
                errors.append(f'Invalid subtotal in product {cart.product.name}')

        if errors:
            raise ValidationError(', '.join(errors))

        return attrs


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            'id',
            'product',
            'sale',
            'name',
            'unit',
            'price',
            'stock',
            'quantity',
            'subtotal',
        ]

