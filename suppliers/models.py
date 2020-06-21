from django.contrib.auth.models import User
from django.db import models

from utils.models import Timestamp


class Supplier(Timestamp):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

