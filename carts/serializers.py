from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from carts.models import Cart


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'product',
            'name',
            'unit',
            'price',
            'stock',
            'quantity',
            'subtotal',
        ]
        read_only_fields = [
            'user',
        ]

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        request = self.context.get('request')
        subtotal = attrs.get('subtotal')
        exists = Cart.objects.filter(product=product, user=request.user).exists()

        if (product.stock - quantity) <= 0:
            raise ValidationError('Stock not enough!')

        if exists:
            raise ValidationError('Your item has been added!')

        if subtotal != (quantity * product.price):
            raise ValidationError('Subtotal not valid!')

        return attrs


