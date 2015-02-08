# python
import csv

# django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

# extranet
import forms
from models import Hours


# === utils ===

def login(request):
    return render(request, 'extranet/login.html')


# === views ===

@login_required
def home(request):
    return render(request, 'extranet/home.html')


@login_required
def hours(request):
    _valid_rows, failed_rows = [], []
    valid_objs, created_objs = [], []

    if request.method == 'POST':

        form = forms.HoursUploadForm(request.user, request.POST, request.FILES)

        if form.is_valid():

            is_preview = 'preview' in request.POST

            # get coder
            coder_id = int(form.cleaned_data['assign_hours_to'])
            coder = User.objects.get(pk=coder_id) if coder_id else request.user

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
        form = forms.HoursUploadForm(request.user)

    d = dict(
        form=form,
        total_hours=sum(h.amount for h in request.user.hours_set.all()),
        failed_rows=failed_rows,
        valid_objs=valid_objs,
        created_objs=created_objs,
    )

    return render(request, 'extranet/hours.html', d)
