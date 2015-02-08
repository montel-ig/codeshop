# django
from django.db import models


class HoursReporter(object):

    def iter_hours(self):
        raise NotImplementedError()

    def total_hours(self):
        return sum(hours.amount for hours in self.iter_hours())


class Nameable(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name
