from django.db import models

from utils.models import Timestamp


class Product(Timestamp):
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name


