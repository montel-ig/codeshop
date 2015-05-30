# python
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

# django
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# 3rd party
import pytz
from github import Github


def _github():
    return Github(settings.GITHUB_ACCESS_TOKEN)


def round_datetime(dt, resolution=60 * 15):
    dt = dt.replace(tzinfo=None)  # make naive
    seconds = (dt - dt.min).seconds
    rounding = (seconds + resolution / 2) // resolution * resolution
    ret = dt + timedelta(0, rounding - seconds, -dt.microsecond)
    return timezone.localtime(ret.replace(tzinfo=pytz.UTC))


class HoursReporter(object):

    def iter_hours(self):
        raise NotImplementedError()

    def iter_hours_by_needs_and_issues(self):
        totals = defaultdict(Decimal)
        contributors = defaultdict(set)

        for hours in self.iter_hours():
            if hours.issue:
                totals[(hours.issue.need, hours.issue)] += hours.amount
                contributors[(hours.issue.need, hours.issue)].add(hours.coder)

        totals_and_coders_by_needs = defaultdict(list)
        for (need, issue), amount in totals.items():
            coders = contributors[(need, issue)]
            totals_and_coders_by_needs[need].append([issue, amount, coders])

        keys = totals_and_coders_by_needs.keys()
        keys.sort(key=lambda x: (
            x is None, (x.project.name, x.name) if x else (None, None)
        ))

        for need in keys:
            issues_with_amounts_and_coders = totals_and_coders_by_needs[need]
            yield (
                need,
                issues_with_amounts_and_coders,
                sum(amount for _, amount, _ in issues_with_amounts_and_coders)
            )

    def iter_hours_with_no_related_issues(self):
        data = defaultdict(list)
        for hours in self.iter_hours():
            if not hours.issue:
                data[hours.tags_string()].append(hours)
        for tags, hours in data.items():
            yield tags, hours, sum(x.amount for x in hours)

    def total_hours(self):
        return sum(hours.amount for hours in self.iter_hours())


class Nameable(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.name == '':
            raise ValidationError('Name is required')
