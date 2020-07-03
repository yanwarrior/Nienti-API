from django.db import transaction
from django.db.models import Sum, F, Value, CharField
from django.db.models.functions import Coalesce, Concat
from django.utils.timezone import now
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.models import Cart
from sales.models import Sale, Item
from sales.serializers import SaleSerializer, ItemSerializer, ItemBestSellerSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by('-created')
    serializer_class = SaleSerializer
    search_fields = [
        'sale_number',
        'customer__name'
    ]
    filterset_fields = {
        'sale_date': ['gte', 'lte',],
        'id': ['exact'],
        'sale_number': ['exact'],
    }

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

        # TODO: update product stock before carts remove or after 
        Item.objects.bulk_create(item_set)
        carts.delete()

    @action(detail=True, methods=['POST'])
    def invoice(self, request, pk=None):
        sale = self.get_object()
        items = sale.sale_items.all()

        column_sale = [
            {'qr': f'{sale.sale_number}@{self.request.user.username}', 'fit': '50'},
            '\n',
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
                'text': '#',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Product',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Price',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Qty',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Subtotal',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            }
        ]

        item_body = []
        counter = 1
        for item in items:
            item_body.append([
                counter,
                item.name,
                "${:,.2f}".format(item.price),
                f'{item.quantity} {item.unit.capitalize()}',
                "${:,.2f}".format(item.subtotal)
            ])
            counter += 1

        doc_def = {
            'content': [
                {
                    'text': 'Sales Order',
                    'alignment': 'center',
                    'color': '#61a948',
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
                        'widths': ['auto', '*', '*', 'auto', '*'],
                        'body': [
                            item_header,
                            *item_body
                        ]
                    }
                },
                '\n\n',
                {
                    'text': 'Payment Detail',
                    'style': 'textMuted',
                },
                {
                    'style': 'tableExample',
                    'layout': 'noBorders',
                    'table': {
                        'widths': ['*'] * 2,
                        'body': [
                            [
                                {
                                    'text': 'Total Price',
                                    'style': 'tableHeader'
                                },
                                {
                                    'text': "${:,.2f}".format(sale.total),
                                    'style': 'green',
                                }
                            ],
                            [
                                {
                                    'text': 'Discount',
                                    'style': 'tableHeader'
                                },
                                {
                                    'text': "${:,.2f}".format(sale.discount),
                                },
                            ],
                            [
                                {
                                    'text': 'Tax',
                                    'style': 'tableHeader'
                                },
                                {
                                    'text': "${:,.2f}".format(sale.tax),
                                },
                            ],
                            [
                                {
                                    'text': 'Grand Total',
                                    'style': 'tableHeader'
                                },
                                {
                                    'text': "${:,.2f}".format(sale.total_after),
                                    'color': 'green'
                                },
                            ]
                        ]
                    }
                },
                '\n\n',
                {'canvas': [ { 'type': 'line', 'x1': 0, 'y1': 0, 'x2': 200, 'y2': 0, 'lineWidth': 1 } ]},
                {
                    'style': 'tableExample',
                    'layout': 'noBorders',
                    'table': {
                        'widths': ['*'] * 2,
                        'body': [
                            [
                                {
                                    'text': 'Pay',
                                    'style': 'tableHeader'
                                },
                                {
                                    'text': "${:,.2f}".format(sale.pay),
                                },
                            ],
                            [
                                {
                                    'text': 'Change',
                                    'style': 'tableHeader'
                                },
                                {
                                    'text': "${:,.2f}".format(sale.change)
                                }
                            ]
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

    @action(methods=['POST'], detail=True)
    def delivery_orders(self, request, pk=None):
        sale = self.get_object()
        items = sale.sale_items.all()

        column_sale = [
            {'qr': f'{sale.sale_number}@{self.request.user.username}', 'fit': '50'},
            '\n',
            {
                'text': f'DO/{sale.sale_number}/{now().strftime("%Y/%m/%d")}',
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
                'text': '#',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Product',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Quantity',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Notes',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            }
        ]

        item_body = []
        counter = 1
        for item in items:
            item_body.append([
                counter,
                item.name,
                f'{item.quantity} {item.unit.capitalize()}',
                ''
            ])

            counter += 1

        doc_def = {
            'content': [
                {
                    'text': 'Delivery Orders',
                    'alignment': 'center',
                    'color': '#61a948',
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
                        'widths': ['auto', '*', '*', '*'],
                        'body': [
                            item_header,
                            *item_body
                        ]
                    }
                },
                '\n\n',
                {
                    'alignment': 'justify',
                    'columns': [
                        [
                            {
                                "text": "Receipt by",
                                "bold": "true",
                            },
                            '\n\n',
                            {
                                "text": "(.....................)",
                                "bold": "true",
                            },
                        ],
                        [
                            {
                                "text": "Best regards",
                                "bold": "true",
                                "alignment": "right",
                            },
                            '\n\n',
                            {
                                "text": "(.....................)",
                                "bold": "true",
                                "alignment": "right",
                            },
                        ]
                    ]
                },
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

    @action(methods=['GET'], detail=False)
    def reports(self, request, pk=None):
        queryset = self.filter_queryset(self.get_queryset())

        sales = queryset.values_list('pk')
        items = Item.objects.filter(sale__in=sales)

        item_summary = items.aggregate(total=Coalesce(Sum('subtotal'), 0))
        item_annotation = items.values(
            'product',
        ).annotate(
            total=Coalesce(Sum('subtotal'), 0),
            quantity=Concat(
                Coalesce(Sum('quantity'), 0),
                Value(' '),
                F('unit'),
                output_field=CharField()
            ),
            name=F('product__name') # Alias 'product__name' to 'name'
        )

        item_header = [
            {
                'text': '#',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Product',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Qty',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            },
            {
                'text': 'Total',
                'style': 'tableHeader',
                'fillColor': '#61a948',
                'color': 'white'

            }
        ]

        item_body = []
        counter = 1
        for item in item_annotation:
            item_body.append([
                counter,
                item.get('name'),
                item.get('quantity'),
                "Rp. {:,.2f}".format(item.get('total'))
            ])

            counter += 1

        doc_def = {
            'content': [
                {
                    'text': 'Sales Orders Report',
                    'alignment': 'center',
                    'color': '#61a948',
                    'style': 'header'
                },
                '\n\n',
                {
                    'columns': [
                        [
                            {
                                'text': 'Period',
                                'alignment': 'left',
                                'style': 'textMuted'
                            },
                            {
                                'text': f'{request.GET.get("sale_date__gte")}'
                                        f' to '
                                        f'{request.GET.get("sale_date__lte")}'
                            }
                        ],
                        [
                            {
                                'text': 'Report Information',
                                'alignment': 'right',
                                'style': 'textMuted'
                            },
                            {
                                'text': 'Total Rp. {:,.2f}'.format(item_summary.get('total')),
                                'alignment': 'right',
                            }
                        ]
                    ]
                },
                '\n',
                {
                    'style': 'tableExample',
                    'table': {
                        'widths': ['auto', '*', '*', '*'],
                        'body': [
                            item_header,
                            *item_body
                        ]
                    }
                },
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


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all().order_by('-created')
    serializer_class = ItemSerializer

    @action(methods=['GET'], detail=False)
    def best_seller(self, request, pk=None):
        queryset = self.get_queryset()
        best_seller_items = queryset.values('product')\
            .annotate(
                sold=Concat(
                    Coalesce(Sum('quantity'), 0),
                    Value(' '),
                    F('unit'),
                    output_field=CharField()
                ),
                sum_quantity=Coalesce(Sum('quantity'), 0),
                name=F('product__name')
            )\
            .filter(sum_quantity__gte=1)\
            .order_by('-sum_quantity')[:5]

        serializer = ItemBestSellerSerializer(data=list(best_seller_items), many=True)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)

