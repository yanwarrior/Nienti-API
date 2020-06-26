from rest_framework import viewsets

from customers.models import Customer
from customers.serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created')
    serializer_class = CustomerSerializer
    search_fields = [
        'name',
        'email',
        'phone',
    ]
