# -*- coding: utf-8 -*-

# python
import calendar
from collections import defaultdict
from datetime import date
from decimal import Decimal

# django
from django.core.urlresolvers import reverse
from django.db import models

# 3rd party
from isoweek import Week

# this package
from utils import HoursReporter
from _coder import Hours, Month


# === mixins ===

class ReportMixin:

    def label(self):
        raise NotImplementedError()

    def get_report_type(self):
        raise NotImplementedError()

    def get_csv_link(self):
        raise NotImplementedError()

    def get_edit_link(self):
        raise NotImplementedError()

    def total_billable_hours(self):
        raise NotImplementedError()


class TimeNavMixin:

    def time_label(self):
        raise NotImplementedError()

    def start_date(self):
        raise NotImplementedError()

    def end_date(self):
        raise NotImplementedError()

    def prev_url(self):
        raise NotImplementedError()

    def next_url(self):
        raise NotImplementedError()


class WeeklyMixin(TimeNavMixin):
    '''
    Requires the following instance attributes: `iso_week`
    '''
    def get_month_obj(self):
        d = self.iso_week.monday()
        return Month.objects.get_or_create(year=d.year, month=d.month)[0]

    # === TimeNavMixin methods ===

    def time_label(self):
        return u'Week {}'.format(self.iso_week.week)

    def start_date(self):
        return self.iso_week.monday()

    def end_date(self):
        return self.iso_week.sunday()


class MonthlyMixin(TimeNavMixin):
    '''
    Requires the following instance attributes: `year`, `month`
    '''

    def yyyy_mm(self):
        return u'{}-{:02d}'.format(self.year, self.month)

    def prev_month(self):
        if self.month == 1:
            return self.year - 1, 12
        else:
            return self.year, self.month - 1

    def next_month(self):
        if self.month == 12:
            return self.year + 1, 1
        else:
            return self.year, self.month + 1

    def get_month_obj(self):
        return Month.objects.get_or_create(year=self.year, month=self.month)[0]

    # === TimeNavMixin methods ===

    def time_label(self):
        return u'{}-{:02d}'.format(self.year, self.month)

    def start_date(self):
        return date(self.year, self.month, 1)

    def end_date(self):
        last_day = calendar.monthrange(self.year, self.month)[1]
        return date(self.year, self.month, last_day)


# === reports for coders ===

class CoderReport(ReportMixin, HoursReporter):

    def __init__(self, coder):
        self.coder = coder

    def current_week_url(self):
        today = date.today()
        year, week = today.isocalendar()[:2]
        return reverse('extranet_coder_weekly', args=[self.coder.user.username,
                                                      year, week])

    def current_month_url(self):
        today = date.today()
        return reverse('extranet_coder_monthly',
                       args=[self.coder.user.username,
                             today.year,
                             today.month])

    # === ReportMixin methods ===

    def label(self):
        return u'{} &lt;{}&gt;'.format(self.coder.user.username,
                                       self.coder.user.email)

    def get_report_type(self):
        return 'coder'


class CoderWeekly(CoderReport, WeeklyMixin):

    def __init__(self, coder, iso_week):
        self.coder = coder
        self.iso_week = iso_week

    # === ReportMixin methods ===
    def total_billable_hours(self):
        q = dict(
            coder_billing_month=self.get_month_obj(),
            date__gte=self.start_date(),
            date__lte=self.end_date(),
        )
        return sum(hours.amount for hours in
                   self.coder.user.hours_set.filter(**q))

    # === TimeNavMixin methods ===

    def prev_url(self):
        prev = self.iso_week - 1
        return reverse('extranet_coder_weekly', args=(self.coder.user.username,
                                                      prev.year, prev.week))

    def next_url(self):
        next = self.iso_week + 1
        return reverse('extranet_coder_weekly', args=(self.coder.user.username,
                                                      next.year, next.week))

    # === HoursReporter methods ===

    def iter_hours(self):
        for hours in self.coder.user.hours_set.filter(
                date__gte=self.start_date(),
                date__lte=self.end_date(),
        ):
            yield hours


class CoderMonthly(CoderReport, MonthlyMixin):

    def __init__(self, coder, year, month):
        self.coder = coder
        self.year = year
        self.month = month

    # === ReportMixin methods ===
    def get_csv_link(self):
        return reverse('extranet_coder_monthly_csv',
                       args=(self.coder.user.username, self.year, self.month))

    def get_edit_link(self):
        return reverse('extranet_coder_monthly_edit',
                       args=(self.coder.user.username, self.year, self.month))

    def total_billable_hours(self):
        q = dict(coder_billing_month=self.get_month_obj())
        return sum(hours.amount for hours in
                   self.coder.user.hours_set.filter(**q))

    # === HoursReporter methods ===

    def iter_hours(self):
        '''
        Also take a look at HoursReporter.iter_hours and the related functions.
        '''
        for hours in self.coder.user.hours_set.filter(
                date__year=self.year,
                date__month=self.month,
        ).order_by('date', 'start_time'):
            yield hours

    # === MonthlyMixin/TimeNavMixin methods ===

    def prev_url(self):
        year, month = self.prev_month()
        return reverse('extranet_coder_monthly',
                       args=(self.coder.user.username, year, month))

    def next_url(self):
        year, month = self.next_month()
        return reverse('extranet_coder_monthly',
                       args=(self.coder.user.username, year, month))


# === reports for projects ===

def month_match(date, month_obj):
    return (date.year, date.month) == (month_obj.year, month_obj.month)


class ProjectReport(ReportMixin, HoursReporter):
    def __init__(self, project):
        self.project = project

    def current_week_url(self):
        today = date.today()
        year, week = today.isocalendar()[:2]
        return reverse('extranet_project_weekly', args=[self.project.name,
                                                        year, week])

    def current_month_url(self):
        today = date.today()
        return reverse('extranet_project_monthly', args=[self.project.name,
                                                         today.year,
                                                         today.month])

    def iter_months(self):
        date_range = self.project.hours_set.all().aggregate(models.Min('date'),
                                                            models.Max('date'))
        start, end = date_range['date__min'], date_range['date__max']

        if start and end:
            ym_start = 12 * start.year + start.month - 1
            ym_end = 12 * end.year + end.month - 1
            for ym in range(ym_start, ym_end + 1):
                y, m = divmod(ym, 12)
                yield ProjectMonthly(self, y, m + 1)

    # === ReportMixin methods ===

    def label(self):
        return u'{}'.format(self.project.name)

    def get_report_type(self):
        return 'project'


class ProjectWeekly(ProjectReport, WeeklyMixin):
    def __init__(self, project, iso_week):
        self.project = project
        self.iso_week = iso_week

    def __unicode__(self):
        return u'{}'.format(self.iso_week)

    # === HoursReporter methods ===

    def iter_hours(self):
        for hours in Hours.objects.filter(date__gte=self.start_date(),
                                          date__lte=self.end_date(),
                                          project=self.project):
            yield hours

    # === MonthlyMixin/TimeNavMixin methods ===

    def prev_url(self):
        prev = self.iso_week - 1
        return reverse('extranet_project_weekly', args=(self.project.name,
                                                        prev.year, prev.week))

    def next_url(self):
        next = self.iso_week + 1
        return reverse('extranet_project_weekly', args=(self.project.name,
                                                        next.year, next.week))


class ProjectMonthly(ProjectReport, MonthlyMixin):
    def __init__(self, project, year, month):
        self.project = project
        self.year = year
        self.month = month

    def iter_hours(self):
        for hours in Hours.objects.filter(date__year=self.year,
                                          date__month=self.month,
                                          project=self.project):
            yield hours

    def iter_hour_summaries(self):
        total = 0

        # headers
        yield 'CATEGORY', 'DESCRIPTION', 'HOURS'
        yield '', '', ''

        # summarize and yield hours with issues
        d = defaultdict(Decimal)
        for (
                need, issues_w_amounts, total_sum
        ) in self.iter_hours_by_needs_and_issues():
            for issue, amount, coders in issues_w_amounts:
                d[need.name if need else issue.title] += amount
                total += amount
        for description, total_hours in d.items():
            yield 'Development work', description, total_hours
        yield '', '', ''

        # summarize and yield hours with no related issues
        d = defaultdict(Decimal)
        for (
                tags, hours_list, total_sum
        ) in self.iter_hours_with_no_related_issues():
            key = 'Work hours tagged w/ {}'.format(tags.upper())
            for hours in hours_list:
                d[key] += hours.amount
                total += hours.amount
        for description, total_hours in d.items():
            yield [
                'Maintenance, administration, meetings, and other work',
                description,
                total_hours,
            ]

        # yield total
        yield '', '', ''
        yield 'TOTAL', '', total

    def __unicode__(self):
        return u'{}-{:02d}'.format(self.year, self.month)

    # === ReportMixin methods ===
    def get_csv_link(self):
        return reverse('extranet_project_monthly_csv',
                       args=(self.project.name, self.year, self.month))

    # === MonthlyMixin/TimeNavMixin methods ===

    def prev_url(self):
        year, month = self.prev_month()
        return reverse('extranet_project_monthly', args=(self.project.name,
                                                         year, month))

    def next_url(self):
        year, month = self.next_month()
        return reverse('extranet_project_monthly', args=(self.project.name,
                                                         year, month))


# === reports for teams ===

class TeamReport(ReportMixin, HoursReporter):
    def __init__(self, team):
        self.team = team

    def iter_projects(self):
        for project in self.team.customer_projects.all().order_by('name'):
            yield project

    # === ReportMixin methods ===

    def label(self):
        return u'{}'.format(self.team.name)

    def get_report_type(self):
        return 'team'


class TeamWeeklyMeeting(TeamReport):
    def __init__(self, team):
        self.team = team
        self.iso_week = Week(*date.today().isocalendar()[:2]) - 1  # last week

    def __unicode__(self):
        return u'{}'.format(self.iso_week)

    def iter_last_week_project_reports(self):
        for project in self.iter_projects():
            yield ProjectWeekly(project, self.iso_week)

    # === HoursReporter methods ===

    def iter_hours(self):
        for project in self.iter_projects():
            for hours in Hours.objects.filter(date__gte=self.start_date(),
                                              date__lte=self.end_date(),
                                              project=project):
                yield hours
