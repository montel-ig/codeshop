# python
import csv

# django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from django.conf import settings
from django.utils import timezone

# 3rd party
from isoweek import Week

# extranet
import forms
from extranet.models import (
    Hours, CoderWeekly, CoderMonthly, Coder, Issue, Timer, Project, HourTag,
    AlreadyStarted
)


# === utils ===

def get_coder(func):
    def wrapper(request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        if (not request.user.is_superuser) and (request.user != user):
            raise Http404()
        return func(request, Coder(user), *args, **kwargs)
    return wrapper


def get_weekly_obj(func):
    def wrapper(request, coder, year, week):
        weekly = CoderWeekly(coder, Week(int(year), int(week)))
        return func(request, weekly)
    return wrapper


def get_monthly_obj(func):
    def wrapper(request, coder, year, month):
        monthly = CoderMonthly(coder, int(year), int(month))
        return func(request, monthly)
    return wrapper


# === views ===

@login_required
@get_coder
@get_weekly_obj
def weekly(request, weekly):
    d = dict(
        coder_weekly=weekly,
    )
    return render(request, 'extranet/coder_weekly.html', d)


@login_required
@get_coder
@get_monthly_obj
def monthly(request, monthly):
    d = dict(
        coder_monthly=monthly,
    )
    return render(request, 'extranet/coder_monthly.html', d)


@login_required
@get_coder
@get_monthly_obj
def monthly_edit(request, monthly):
    d = dict(
        coder_monthly=monthly,
    )
    return render(request, 'extranet/coder_monthly_edit.html', d)


@login_required
@get_coder
@get_monthly_obj
def monthly_edit_row(request, monthly):
    confirmed = (request.method == 'POST')
    d = request.POST if confirmed else request.GET
    obj = Hours.objects.get(id=d['row_id'])

    if d.get('action') == 'delete':
        assert(not obj.coder_billing_month)
        assert(not obj.project_billing_month)
        assert(obj in set(monthly.iter_hours()))
        if confirmed:
            obj.delete()
            return redirect(reverse('extranet_coder_monthly_edit',
                                    args=[monthly.coder.user.username,
                                          monthly.year, monthly.month]))
    d = dict(
        selected=obj,
        coder_monthly=monthly,
    )
    return render(request, 'extranet/coder_monthly_edit.html', d)


@login_required
@get_coder
@get_monthly_obj
def monthly_csv(request, monthly):
    d = dict(
        coder_monthly=monthly,
    )
    response = render(request, 'extranet/coder_monthly.csv', d,
                      content_type='text/csv')
    fn = u'{}-{:02d}-hours-{}.csv'.format(monthly.year, monthly.month,
                                          monthly.coder.user.username)
    response['Content-Disposition'] = u'attachment; filename="{}"'.format(fn)
    return response


@login_required
@get_coder
def upload_hours_as_csv(request, coder):
    _valid_rows, failed_rows = [], []
    valid_objs, created_objs, existing_objs = [], [], []

    if request.method == 'POST':

        form = forms.HoursUploadForm(request.POST, request.FILES)

        if form.is_valid():
            skip_failed_rows = form.cleaned_data['skip_failed_rows']
            is_preview = 'preview' in request.POST

            # parse rows
            rows = csv.reader(request.FILES['file'],
                              delimiter=str(form.cleaned_data['delimiter']),
                              quotechar='"')
            for row in rows:
                if not row:
                    continue
                try:
                    obj = Hours.objects._csv_parse(row, coder=coder)
                except Exception, e:
                    failed_rows.append(row + [e])
                else:
                    _valid_rows.append(row)
                    if is_preview:
                        obj.as_scsv()  # make sure dump to csv works
                        if obj.similar_row_exists():
                            existing_objs.append(obj)
                        else:
                            valid_objs.append(obj)

            # create objects
            if not is_preview and (not failed_rows or skip_failed_rows):

                for row in _valid_rows:
                    obj, created = Hours.objects.csv_get_or_create(row,
                                                                   coder=coder)
                    if created:
                        created_objs.append(obj)
                    else:
                        existing_objs.append(obj)

    else:
        form = forms.HoursUploadForm()

    d = dict(
        coder=coder,
        form=form,
        failed_rows=failed_rows,
        valid_objs=valid_objs,
        existing_objs=existing_objs,
        created_objs=created_objs,
    )

    return render(request, 'extranet/upload_hours_as_csv.html', d)


@login_required
@get_coder
def timer(request, coder):
    obj, created = Timer.objects.get_or_create(coder=coder.user)

    if request.method == 'POST':
        timer = coder.user.timer
        do = request.POST.get('do', None)
        if do == 'start':
            obj.start_issue(Issue.objects.get(pk=request.POST.get('issue_id')))
        elif do == 'start_non_ticketed':
            project = Project.objects.get(name=request.POST.get('project'))
            assert(project in coder.projects)
            tag = HourTag.objects.get(name=request.POST.get('tag'))
            obj.start_non_ticketed(project, tag)
        elif do == 'start_again':
            hours = Hours.objects.get(pk=int(request.POST.get('hours_id')))
            try:
                obj.start_again(hours)
            except AlreadyStarted:
                # by default, don't let new timer starts override an already
                # running timer instance
                pass
        elif do == 'tag':
            timer.add_tag(request.POST.get('tag'))
        elif do == 'deltag':
            timer.del_tag(request.POST.get('tag'))
        elif do == 'stop':
            timer.stop()

        # times
        elif do == 'incr_start':
            timer.increase_start()
        elif do == 'decr_start':
            timer.decrease_start()
        elif do == 'incr_end':
            timer.increase_end()
        elif do == 'decr_end':
            timer.decrease_end()

        # amount
        elif do == 'incr_amount':
            timer.increase_amount()
        elif do == 'decr_amount':
            timer.decrease_amount()
        elif do == 'comment':
            timer.comment = request.POST.get('comment')
            timer.save()
        elif do == 'commit':
            timer.comment = request.POST.get('comment')
            timer.save_values()
            timer.delete()
        elif do == 'delete':
            timer.delete()
        return redirect(reverse('extranet_timer', args=[coder.user.username]))

    timezone.activate(settings.TIME_ZONE)

    d = dict(coder=coder, timer=obj)
    return render(request, 'extranet/timer.html', d)
