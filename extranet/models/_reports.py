# python
from collections import defaultdict
from datetime import date

# django
from django.core.urlresolvers import reverse
from django.db import models

# this package
from utils import HoursReporter
from _issues import Issue
from _hours import Hours


class WeeklyHours(HoursReporter):

    def __init__(self, coder, iso_week):
        self.coder = coder
        self.iso_week = iso_week

    def prev_week_url(self):
        prev = self.iso_week - 1
        return reverse('extranet_weekly_hours', args=(self.coder.username,
                                                      prev.year, prev.week))

    def next_week_url(self):
        next = self.iso_week + 1
        return reverse('extranet_weekly_hours', args=(self.coder.username,
                                                      next.year, next.week))

    def iter_hours(self):
        '''
        Also take a look at HoursReporter.iter_hours and the related functions.
        '''
        for hours in self.coder.hours_set.filter(
                date__gte=self.iso_week.monday(),
                date__lte=self.iso_week.sunday()
        ):
            yield hours




def month_match(date, month_obj):
    return (date.year, date.month) == (month_obj.year, month_obj.month)


class MonthlyReport(HoursReporter):
    def __init__(self, project, year, month):
        self.project = project
        self.year = year
        self.month = month

    def two_digit_month(self):
        return u'{:02d}'.format(self.month)

    def first_of_this_month(self):
        return date(self.year, self.month, 1)

    def first_of_next_month(self):
        this = self.first_of_this_month()
        if this.month == 12:
            return this.replace(year=this.year+1, month=1)
        else:
            return this.replace(month=this.month + 1)

    def iter_hours(self):
        for hours in Hours.objects.filter(date__gte=self.first_of_this_month(),
                                          date__lt=self.first_of_next_month(),
                                          project=self.project):
            yield hours

    def __unicode__(self):
        return u'{}-{:02d}'.format(self.year, self.month)


class ProjectReport:
    def __init__(self, project):
        self.project = project

    def iter_months(self):
        date_range = self.project.hours_set.all().aggregate(models.Min('date'),
                                                            models.Max('date'))
        start, end = date_range['date__min'], date_range['date__max']

        if start and end:
            ym_start = 12 * start.year + start.month - 1
            ym_end = 12 * end.year + end.month - 1
            for ym in range(ym_start, ym_end + 1):
                y, m = divmod(ym, 12)
                yield MonthlyReport(self, y, m + 1)
