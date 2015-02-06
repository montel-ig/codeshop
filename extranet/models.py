# python
from datetime import datetime, timedelta

# django
from django.contrib.auth.models import Group, User
from django.db import models

# 3rd party
from github import Github


class HoursReporter(object):

    def iter_hours(self):
        raise NotImplementedError()

    def total_hours(self):
        return sum(hours.amount for hours in self.iter_hours())


# === models for representing customer projects ===

class Nameable(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class Project(Nameable, HoursReporter):
    customer_team = models.ForeignKey(Group, related_name='code_projects')
    coder_team = models.ForeignKey(Group, related_name='customer_projects')

    def iter_hours(self):
        for need in self.need_set.all():
            for hours in need.iter_hours():
                yield hours

    def latest_need(self):
        return self.need_set.order_by('-created_at').first()


class Need(Nameable, HoursReporter):
    customer = models.ForeignKey(Project)
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


# === github models ===

def _github():
    token = open('github-access-token.txt').read().strip()
    return Github(token)


class Syncable(models.Model):
    synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def _update_sync_timestamp(self, save=True):
        '''
        Silly implementation for updating the sync timestamp.

        Basically we let the sync timestamp lag one day behind the real
        timestamp, to make sure no updates are lost because of timezone
        differences or other peculiarities.
        '''
        self.synced_at = datetime.now() - timedelta(1)
        if save:
            self.save()


class Organization(models.Model):
    # github fields
    login = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Github organization'

    def __unicode__(self):
        return self.login

    def iter_hours(self):
        for repo in self.repository_set.all():
            for hours in repo.iter_hours():
                yield hours

    def repositories_string(self):
        return u', '.join(x.name for x in self.repository_set.all())


class Repository(Syncable, HoursReporter):
    # github fields
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Github repository'
        verbose_name_plural = 'Github repositories'

    def __unicode__(self):
        return self.get_distinct_name()

    def _iter_unsynced_issue_data(self):
        q = dict(state='all')

        if self.synced_at:
            q['since'] = self.synced_at

        for d in _github().get_repo(self.get_distinct_name()).get_issues(**q):
            yield d

    def _sync(self):
        """
        Fetches recent issues for a repository, creates the related objects,
        and syncs the issue data.
        """
        for d in self._iter_unsynced_issue_data():
            issue, created = Issue.objects.get_or_create(repository=self,
                                                         number=d.number)
            issue._sync_data(d)

        self._update_sync_timestamp(save=False)
        self.save()

    def get_distinct_name(self):
        return u'{self.organization.login}/{self.name}'.format(self=self)

    def iter_hours(self):
        for issue in self.issue_set.all():
            for hours in issue.iter_hours():
                yield hours

    def latest_closed_issue(self):
        return self.issue_set.all().order_by('-closed_at').first()

    def latest_created_issue(self):
        return self.issue_set.all().order_by('-created_at').first()

    def latest_updated_issue(self):
        return self.issue_set.all().order_by('-updated_at').first()


class Issue(Syncable, HoursReporter):
    # github fields
    repository = models.ForeignKey(Repository)
    number = models.IntegerField()
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    html_url = models.URLField(null=True)

    # non-github fields
    need = models.ForeignKey(Need, null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=3, decimal_places=1,
                                          blank=True, null=True)
    estimated_on = models.DateField(null=True, blank=True)
    work_initiated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Github issue'

    def __unicode__(self):
        return u'{}: {}'.format(self.repository, self.title)

    def _sync_data(self, d):
        FIELDS = ['title', 'created_at', u'updated_at', 'closed_at',
                  'html_url']
        for attr in FIELDS:
            setattr(self, attr, getattr(d, attr))
        self._update_sync_timestamp(save=False)
        self.save()

    def iter_hours(self):
        for hours in self.hours_set.all():
            yield hours


# === hour reports ===

class Hours(models.Model):

    customer = models.ForeignKey(Project)
    date = models.DateField()
    amount = models.DecimalField(max_digits=4, decimal_places=2)
    coder = models.ForeignKey(User)

    issue = models.ForeignKey(Issue, null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    start_time = models.DateField(null=True, blank=True)
    end_time = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Hours'
