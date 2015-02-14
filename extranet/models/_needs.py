# django
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models

# this package
from .utils import HoursReporter, Nameable


class Project(Nameable, HoursReporter):
    customer_team = models.ForeignKey(Group, related_name='code_projects')
    coder_team = models.ForeignKey(Group, related_name='customer_projects')

    def get_absolute_url(self):
        return reverse('extranet_project', args=[self.name])

    def is_coder_team_member(self, user):
        return user in self.coder_team.user_set.all()

    def iter_hours(self):
        for hours in self.hours_set.all():
            yield hours

    def latest_need(self):
        return self.need_set.order_by('-created_at').first()

    def repositories_string(self):
        return u', '.join(x.name for x in self.repository_set.all())


class Need(models.Model, HoursReporter):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project)

    description = models.TextField(default='', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_estimate_requested = models.BooleanField(default=False)
    estimate_finished_at = models.DateTimeField(null=True, blank=True,
                                                default=None)
    estimate_approved_at = models.DateTimeField(null=True, blank=True,
                                                default=None)

    def __unicode__(self):
        return u'{}: {}'.format(self.project, self.name)

    def calculate_estimate(self):
        return sum(x.estimated_hours for x in self.issue_set.all())

    def iter_hours(self):
        for issue in self.issue_set.all():
            for hours in issue.iter_hours():
                yield hours

    def all_issues_closed_at(self):
        ''' None means at least one related issue is still not closed '''
        latest = None
        for this in self.issue_set.all():
            if not this.closed_at:
                return None
            else:
                latest = (max(latest, this.closed_at)
                          if latest
                          else this.closed_at)
        # else
        return latest

    def first_issue_started_at(self):
        ''' None means that no related issues have been started yet '''
        started = None
        for this in self.issue_set.all():
            val = this.work_initiated_at or this.closed_at
            if val:
                started = min(started, val) if started else val
        return started
