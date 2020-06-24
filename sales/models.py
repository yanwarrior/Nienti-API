from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from products.models import Product
from utils.models import Timestamp


class Sale(Timestamp):
    sale_number = models.CharField(max_length=100, unique=True)
    sale_date = models.DateField(default=now)
    note = models.TextField(blank=True, null=True)
    total = models.PositiveIntegerField(default=0)
    pay = models.PositiveIntegerField(default=0)
    change = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, related_name='user_sales', on_delete=models.SET_NULL, null=True)
    tax = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.sale_number


class Item(Timestamp):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='product_items', null=True)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='sale_items')
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Cart(Timestamp):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='product_carts', null=True)
    user = models.ForeignKey(User, related_name='user_carts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

