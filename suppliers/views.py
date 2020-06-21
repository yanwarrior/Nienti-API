from rest_framework import viewsets

from suppliers.models import Supplier
from suppliers.serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-created')
    serializer_class = SupplierSerializer
    search_fields = ['name', 'phone']
    filterset_fields = ['id']



