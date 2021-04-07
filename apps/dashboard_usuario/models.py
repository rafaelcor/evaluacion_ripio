from django.db import models
from django.contrib.auth.models import User

import datetime

# Create your models here.


class Currency(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    value = models.FloatField(default=0.0)


class Transaction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        abstract = True


class MoneyDelivery(Transaction):
    origin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_as_origin")
    destiny_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions_as_destiny")
    value = models.FloatField(default=0.0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class MoneyDeliveryLock(models.Model):
    origin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="money_delivery_lock")
    locked = models.BooleanField(default=False)