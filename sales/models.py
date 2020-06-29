from django.db import models
from django.utils.timezone import now
from rest_framework_simplejwt.state import User

from customers.models import Customer
from products.models import Product
from utils.models import Timestamp


class Sale(Timestamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sales')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_sales')
    sale_number = models.CharField(max_length=100, unique=True)
    sale_date = models.DateField(default=now)
    total = models.PositiveIntegerField()
    total_after = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    tax = models.PositiveIntegerField(default=1400)
    pay = models.PositiveIntegerField()
    change = models.PositiveIntegerField()

    def __str__(self):
        return self.sale_number


class Item(Timestamp):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_items')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_items')
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return self.name
