from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=True, methods=['POST'])
    def invoice(self, request, pk=None):
        sale = self.get_object()
        items = sale.sale_items.all()

        column_sale = [
            {
                'text': sale.sale_number,
                'style': 'subheader'
            },
            {
                'text': sale.sale_date,
                'style': 'textMuted',
            }
        ]

        column_customer = [
            {
                'alignment': 'right',
                'text': sale.customer.name,
                'style': 'subheader'
            },
            {
                'alignment': 'right',
                'text': sale.customer.phone,
                'style': 'textMuted'
            },
            {
                'alignment': 'right',
                'text': sale.customer.address,
                'style': 'textMuted'
            },
        ]

        item_header = [
            {
                'text': 'Product',
                'style': 'tableHeader',
                'fillColor': 'green',
                'color': 'white'

            },
            {
                'text': 'Price',
                'style': 'tableHeader',
                'fillColor': 'green',
                'color': 'white'

            },
            {
                'text': 'Quantity',
                'style': 'tableHeader',
                'fillColor': 'green',
                'color': 'white'

            },
            {
                'text': 'Subtotal',
                'style': 'tableHeader',
                'fillColor': 'green',
                'color': 'white'

            }
        ]

        item_body = []
        for item in items:
            item_body.append([item.name, "${:,.2f}".format(item.price), item.quantity, "${:,.2f}".format(item.subtotal)])

        doc_def = {
            'content': [
                {
                    'text': 'Sales Order',
                    'alignment': 'center',
                    'style': 'header'
                },
                '\n\n',
                {
                    'alignment': 'justify',
                    'columns': [column_sale, column_customer],
                },
                '\n',
                {
                    'style': 'tableExample',
                    'table': {
                        'widths': ['*'] * 4,
                        'body': [
                            item_header,
                            *item_body
                        ]
                    }
                }
            ],
            'styles': {
                'header': {
                    'fontSize': 20,
                    'bold': True
                },
                'subheader': {
                    'fontSize': 15,
                    'bold': True
                },
                'textMuted': {
                    'fontSize': 12,
                    'color': 'gray'
                },
                'quote': {
                    'italics': True
                },
                'small': {
                    'fontSize': 8
                },
                'tableExample': {
                    'margin': [0, 5, 0, 15],

                },
                'tableHeader': {
                    'bold': True,
                    'fontSize': 13,
                    'color': 'black',
                }
            },
        }

        return Response(doc_def)
