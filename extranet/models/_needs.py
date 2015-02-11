# django
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models

# this package
from .utils import HoursReporter, Nameable


class Project(Nameable, HoursReporter):
    customer_team = models.ForeignKey(Group, related_name='code_projects')
    coder_team = models.ForeignKey(Group, related_name='customer_projects')

    def iter_hours(self):
        for hours in self.hours_set.all():
            yield hours

    def get_customer_url(self):
        return reverse('extranet_monthly_report', args=[self.name])

    def latest_need(self):
        return self.need_set.order_by('-created_at').first()

    def repositories_string(self):
        return u', '.join(x.name for x in self.repository_set.all())


class Need(models.Model, HoursReporter):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project)
    created_at = models.DateTimeField(auto_now_add=True)
    is_estimate_requested = models.BooleanField(default=False)
    estimate_finished_at = models.DateTimeField(null=True, blank=True,
                                                default=None)
    estimate_approved_at = models.DateTimeField(null=True, blank=True,
                                                default=None)

    def iter_hours(self):
        for issue in self.issue_set.all():
            for hours in issue.iter_hours():
                yield hours

    def __unicode__(self):
        return u'{}: {}'.format(self.project, self.name)
