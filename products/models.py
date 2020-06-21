from django.db import models

from utils.models import Timestamp


class Product(Timestamp):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


