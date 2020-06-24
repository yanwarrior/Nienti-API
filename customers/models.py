from django.contrib.auth.models import User
from django.db import models

from utils.models import Timestamp


class Customer(Timestamp):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

