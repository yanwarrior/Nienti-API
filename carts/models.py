from django.contrib.auth.models import User
from django.db import models

from products.models import Product
from utils.models import Timestamp


class Cart(Timestamp):
    user = models.ForeignKey(User, related_name='user_carts', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_carts', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.product.name