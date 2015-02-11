# python
from collections import defaultdict
from decimal import Decimal

# django
from django.db import models


class HoursReporter(object):

    def iter_hours(self):
        raise NotImplementedError()

    def iter_hours_by_needs_and_issues(self):
        totals = defaultdict(Decimal)

        for hours in self.iter_hours():
            if hours.issue:
                totals[(hours.issue.need, hours.issue)] += hours.amount

        totals_by_needs = defaultdict(list)
        for (need, issue), amount in totals.items():
            totals_by_needs[need].append([issue, amount])

        keys = totals_by_needs.keys()
        keys.sort(key=lambda x: (x is None, x.name if x else None))

        for need in keys:
            issues_with_amounts = totals_by_needs[need]
            yield need, issues_with_amounts

    def iter_hours_with_no_related_issues(self):
        data = defaultdict(list)
        for hours in self.iter_hours():
            if not hours.issue:
                data[hours.tags_string()].append(hours)
        for tags, hours in data.items():
            yield tags, hours

    def total_hours(self):
        return sum(hours.amount for hours in self.iter_hours())


class Nameable(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name
