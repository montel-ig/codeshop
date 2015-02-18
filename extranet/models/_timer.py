# python
import csv
import math
import StringIO
from datetime import timedelta
from decimal import Decimal

# django
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# this package
from extranet.models import Project, HourTag, Repository, Issue, Hours
from .utils import round_datetime


class AlreadyStarted(Exception):
    pass


class AlreadyStopped(Exception):
    pass


class NotStarted(Exception):
    pass


def tz_date(datetime_):
    return timezone.localtime(datetime_).date()


def tz_time(datetime_):
    return timezone.localtime(datetime_).time()


def dt_up(dt):
    tmp = round_datetime(dt, resolution=settings.TIMER_STEP_SIZE)
    if tmp <= dt:
        tmp += timedelta(0, settings.TIMER_STEP_SIZE)
    return tmp


def dt_down(dt):
    tmp = round_datetime(dt, resolution=settings.TIMER_STEP_SIZE)
    if tmp >= dt:
        tmp -= timedelta(0, settings.TIMER_STEP_SIZE)
    return tmp


class Timer(models.Model):
    # key timer fields
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    # required by Hours
    coder = models.OneToOneField(User)
    project = models.ForeignKey(Project, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=4, decimal_places=2, blank=True,
                                 null=True)

    # special, at least one required
    tags = models.ManyToManyField(HourTag, blank=True, null=True)

    # optional for Hours
    repository = models.ForeignKey(Repository, null=True, blank=True)
    issue = models.ForeignKey(Issue, null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    def add_tag(self, tag):
        obj = HourTag.objects.get(name=tag)
        self.tags.add(obj)
        self.save()

    def del_tag(self, tag):
        obj = HourTag.objects.get(name=tag)
        self.tags.remove(obj)
        self.save()

    def calculate_amount_absolute(self):
        end = self.end_time or timezone.now()
        d = end - self.start_time
        seconds = d.days * (24 * 3600) + d.seconds
        hours = seconds / Decimal('3600.0')
        return Decimal('{}'.format(hours))

    def calculate_amount_absolute_hhmmss(self):
        end = self.end_time or timezone.now()
        d = end - self.start_time
        h, m, s = d.seconds // 3600, (d.seconds // 60) % 60, d.seconds % 60

        ret = u' {:2d}s'.format(s) if not self.end_time else u''
        if d.days or h or m:
            ret = u'{:2d}m'.format(m) + ret
        if d.days or h:
            ret = u'{:2d}h '.format(h) + ret
        if d.days:
            ret = u'{:2d}d '.format(d.days) + ret
        return ret

    def calculate_amount_billable(self):

        hour_steps = settings.TIMER_STEPS
        headroom_step = settings.TIMER_HEADROOM

        end = self.end_time or timezone.now()

        d = end - self.start_time

        # calculate hours
        seconds = d.days * (24 * 3600) + d.seconds
        hours = seconds / Decimal('3600.0')

        # subtract `headroom_step` to give some headroom before rounding up
        #
        # e.g., with hour step 4.0 and headroom 20.0, we could say that we
        # round up to the next 15 mins after at least 3 mins has passed, or in
        # other words: "the first three minutes are free"
        hours -= Decimal('1.0') / headroom_step

        # round to next step
        next_step_value = Decimal(math.ceil(hours * hour_steps)) / hour_steps

        value = Decimal('{}'.format(next_step_value))

        # don't return -0.0
        value = value or Decimal('0.0')

        return value

    def get_available_tags(self):
        selected = self.tags.all()
        return [x for x in HourTag.objects.all() if x not in selected]

    def save_values(self):
        scsv = self.as_scsv()
        f = StringIO.StringIO(scsv)
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            obj, created = Hours.objects.csv_get_or_create(row)
            obj.save()

    def get_end_time(self):
        return self.end_time or timezone.now()

    def _recalculate_amount(self):
        ''' doesn't save '''
        if self.amount is not None:
            self.amount = self.calculate_amount_billable()

    def increase_start(self):
        dt = dt_up(self.start_time)
        if dt < self.get_end_time():
            self.start_time = dt
            self._recalculate_amount()
            self.save()

    def decrease_start(self):
        self.start_time = dt_down(self.start_time)
        self._recalculate_amount()
        self.save()

    def increase_end(self):
        self.end_time = dt_up(self.end_time)
        self._recalculate_amount()
        self.save()

    def decrease_end(self):
        dt = dt_down(self.end_time)
        if dt > self.start_time:
            self.end_time = dt
            self._recalculate_amount()
            self.save()

    def increase_amount(self):
        step = Decimal('1.0') / settings.TIMER_STEPS
        self.amount += step
        self.save()

    def is_ready(self):
        return (self.end_time and self.tags.all())

    def decrease_amount(self):
        step = Decimal('1.0') / settings.TIMER_STEPS
        self.amount -= step
        self.amount = max(self.amount, Decimal('0.0'))
        self.save()

    def prepare_hours_object(self):
        d = dict(
            # required
            coder=self.coder,
            project=self.project,
            date=tz_date(self.start_time),
            amount=self.amount or '',
            # optional
            start_time=tz_time(self.start_time),
            end_time=tz_time(self.get_end_time()),
            issue=self.issue,
            repository=self.repository,
            comment=self.comment,
        )

        obj = Hours(**d)
        obj._tags_to_be = [x.name for x in self.tags.all()]

        return obj

    def start_issue(self, issue):
        if self.start_time:
            raise AlreadyStarted()
        self.issue = issue
        self.repository = issue.repository
        self.project = issue.repository.default_project
        self.start_time = timezone.now()
        self.save()

    def stop(self):
        if self.end_time:
            raise AlreadyStopped()
        if not self.start_time:
            raise NotStarted()
        self.end_time = timezone.now()
        self.amount = self.calculate_amount_billable()
        self.save()

    def as_scsv(self):
        if self.start_time:
            return self.prepare_hours_object().as_scsv()
