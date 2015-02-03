from django.db import models


class Mixin(object):
    def __unicode__(self):
        return self.name


class Customer(models.Model, Mixin):
    name = models.CharField(max_length=100)


class Need(models.Model, Mixin):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=200)
    is_estimate_requested = models.BooleanField(default=False)
    estimate_finished_at = models.DateTimeField(null=True, default=None)
    estimate_approved_at = models.DateTimeField(null=True, default=None)
