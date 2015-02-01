from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)


class Need(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=200)
