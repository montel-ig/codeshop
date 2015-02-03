from django.contrib.auth.models import Group
from django.db import models


class Mixin(object):
    def __unicode__(self):
        return self.name


class Need(models.Model, Mixin):
    customer = models.ForeignKey(Group)
    name = models.CharField(max_length=200)
    is_estimate_requested = models.BooleanField(default=False)
    estimate_finished_at = models.DateTimeField(null=True, default=None)
    estimate_approved_at = models.DateTimeField(null=True, default=None)
