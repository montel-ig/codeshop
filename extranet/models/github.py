from django.db import models


from .customer import Need


class Issue(models.Model):
    need = models.ForeignKey(Need)
    estimated_hours = models.DecimalField(max_digits=3, decimal_places=1,
                                          blank=True, null=True)
    estimated_on = models.DateField(null=True, blank=True)
