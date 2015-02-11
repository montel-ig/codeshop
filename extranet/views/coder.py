# python
import csv

# django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# 3rd party
from isoweek import Week

# extranet
import forms
from extranet.models import Hours, WeeklyHours


# === utils ===

def get_coder(func):
    def wrapper(request, username=None):
        if username:
            coder = get_object_or_404(User, username=username)
            if (not request.user.is_superuser) and (request.user != coder):
                raise Http404()
        else:
            coder = request.user
        return func(request, coder)
    return wrapper


def get_weekly_obj(func):
    def wrapper(request, username, year, week):
        if username:
            coder = get_object_or_404(User, username=username)
            if (not request.user.is_superuser) and (request.user != coder):
                raise Http404()
        else:
            coder = request.user
        weekly = WeeklyHours(coder, Week(int(year), int(week)))
        return func(request, weekly)
    return wrapper


# === views ===

@login_required
@get_weekly_obj
def weekly_hours(request, weekly):
    d = dict(
        weekly=weekly,
    )
    return render(request, 'extranet/weekly_hours.html', d)


@login_required
@get_coder
def upload_hours_as_csv(request, coder):
    _valid_rows, failed_rows = [], []
    valid_objs, created_objs = [], []

    if request.method == 'POST':

        form = forms.HoursUploadForm(request.POST, request.FILES)

        if form.is_valid():

            is_preview = 'preview' in request.POST

            # parse rows
            rows = csv.reader(request.FILES['file'],
                              delimiter=str(form.cleaned_data['delimiter']),
                              quotechar='"')
            for row in rows:
                try:
                    obj = Hours.objects._csv_parse(row, coder=coder)
                except Exception, e:
                    failed_rows.append(row + [e])
                else:
                    _valid_rows.append(row)
                    if is_preview:
                        obj.as_scsv()
                        valid_objs.append(obj)

            # create objects
            if not is_preview and not failed_rows:

                for row in _valid_rows:
                    obj, created = Hours.objects.csv_get_or_create(row,
                                                                   coder=coder)
                    if created:
                        created_objs.append(obj)
                    else:
                        valid_objs.append(obj)

    else:
        form = forms.HoursUploadForm()

    d = dict(
        coder=coder,
        form=form,
        total_hours=sum(h.amount for h in coder.hours_set.all()),
        failed_rows=failed_rows,
        valid_objs=valid_objs,
        created_objs=created_objs,
    )

    return render(request, 'extranet/upload_hours_as_csv.html', d)
