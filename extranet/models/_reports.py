# python
import calendar
from datetime import date

# django
from django.core.urlresolvers import reverse
from django.db import models

# this package
from utils import HoursReporter
from _hours import Hours


# === mixins ===

class ReportMixin:

    def label(self):
        raise NotImplementedError()

    def is_coder_report(self):
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
        return reverse('extranet_coder_weekly', args=[self.coder.username,
                                                      year, week])

    def current_month_url(self):
        today = date.today()
        return reverse('extranet_coder_monthly', args=[self.coder.username,
                                                       today.year,
                                                       today.month])

    # === ReportMixin methods ===

    def label(self):
        return u'{} &lt;{}&gt;'.format(self.coder.username, self.coder.email)

    def is_coder_report(self):
        return True


class CoderWeekly(CoderReport, WeeklyMixin):

    def __init__(self, coder, iso_week):
        self.coder = coder
        self.iso_week = iso_week

    # === TimeNavMixin methods ===

    def prev_url(self):
        prev = self.iso_week - 1
        return reverse('extranet_coder_weekly', args=(self.coder.username,
                                                      prev.year, prev.week))

    def next_url(self):
        next = self.iso_week + 1
        return reverse('extranet_coder_weekly', args=(self.coder.username,
                                                      next.year, next.week))

    # === HoursReporter methods ===

    def iter_hours(self):
        for hours in self.coder.hours_set.filter(
                date__gte=self.start_date(),
                date__lte=self.end_date(),
        ):
            yield hours


class CoderMonthly(CoderReport, MonthlyMixin):

    def __init__(self, coder, year, month):
        self.coder = coder
        self.year = year
        self.month = month

    # === HoursReporter methods ===

    def iter_hours(self):
        '''
        Also take a look at HoursReporter.iter_hours and the related functions.
        '''
        for hours in self.coder.hours_set.filter(
                date__year=self.year,
                date__month=self.month,
        ):
            yield hours

    # === MonthlyMixin/TimeNavMixin methods ===

    def prev_url(self):
        year, month = self.prev_month()
        return reverse('extranet_coder_monthly', args=(self.coder.username,
                                                       year, month))

    def next_url(self):
        year, month = self.next_month()
        return reverse('extranet_coder_monthly', args=(self.coder.username,
                                                       year, month))


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

    def is_coder_report(self):
        return True


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

    def __unicode__(self):
        return u'{}-{:02d}'.format(self.year, self.month)

    # === MonthlyMixin/TimeNavMixin methods ===

    def prev_url(self):
        year, month = self.prev_month()
        return reverse('extranet_project_monthly', args=(self.project.name,
                                                         year, month))

    def next_url(self):
        year, month = self.next_month()
        return reverse('extranet_project_monthly', args=(self.project.name,
                                                         year, month))
