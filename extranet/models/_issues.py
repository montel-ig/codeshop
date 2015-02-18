# python
from datetime import timedelta

# django
from django.conf import settings
from django.db import models
from django.utils import timezone

# 3rd party
from github import Github

# this package
from ._needs import Project, Need
from .utils import HoursReporter


# === utils ===

def _github():
    return Github(settings.GITHUB_ACCESS_TOKEN)


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
        self.synced_at = timezone.now() - timedelta(1)
        if save:
            self.save()


# === managers ===

class RepositoryManager(models.Manager):
    def try_to_get_by_name(self, name):
        if name:
            if '/' in name:
                org_login, repo_name = name.split('/')
                return Repository.objects.get(organization__login=org_login,
                                              name=repo_name)
            else:
                return Repository.objects.get(name=name)


# === models ===

class Organization(models.Model, HoursReporter):
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

    objects = RepositoryManager()

    # github fields
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=100)

    # non-github fields
    default_project = models.ForeignKey(Project, null=True, blank=True)

    class Meta:
        verbose_name = 'Github repository'
        verbose_name_plural = 'Github repositories'

    def __unicode__(self):
        return self.name

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

    def try_to_get_issue(self, string_or_int):
        if string_or_int:
            if isinstance(string_or_int, int):
                number = string_or_int
            else:
                number = int(string_or_int.replace('#', ''))
            return Issue.objects.get(repository=self, number=number)

    def iter_hours(self):
        for hours in self.hours_set.all():
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
    assignee_login = models.CharField(max_length=100, null=True, blank=True)

    # non-github fields
    need = models.ForeignKey(Need, null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=3, decimal_places=1,
                                          blank=True, null=True)
    estimated_at = models.DateTimeField(null=True, blank=True)
    work_initiated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Github issue'

    def __unicode__(self):
        return u'{}#{}'.format(self.repository, self.number)

    def _sync_data(self, d):
        FIELDS = ['title', 'created_at', u'updated_at', 'closed_at',
                  'html_url']
        for attr in FIELDS:
            setattr(self, attr, getattr(d, attr))
        self.assignee_login = d.assignee.login if d.assignee else None
        self._update_sync_timestamp(save=False)
        self.save()

    def try_to_get_project(self):
        return (self.need.project
                if self.need
                else self.repository.default_project)

    def iter_hours(self):
        for hours in self.hours_set.all():
            yield hours
