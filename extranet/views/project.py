# django
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# 3rd party
from isoweek import Week

# extranet
from extranet.models import (Project, ProjectReport, ProjectMonthly,
                             ProjectWeekly)


# === utils ===

def get_project(func):
    def wrapper(request, project_name, *args, **kwargs):
        project = get_object_or_404(Project, name=project_name)
        if (
                not request.user.is_superuser
                and not request.user in project.customer_team.user_set.all()
        ):
            raise Http404()
        return func(request, project, *args, **kwargs)
    return wrapper


def get_weekly_obj(func):
    def wrapper(request, project, year, week):
        weekly = ProjectWeekly(project, Week(int(year), int(week)))
        return func(request, weekly)
    return wrapper


def get_monthly_obj(func):
    def wrapper(request, project, year, month):
        monthly = ProjectMonthly(project, int(year), int(month))
        return func(request, monthly)
    return wrapper


# === views ===

@login_required
@get_project
@get_weekly_obj
def weekly(request, report):
    d = dict(
        project_weekly=report,
    )
    return render(request, 'extranet/project_weekly.html', d)


@login_required
@get_project
@get_monthly_obj
def monthly(request, report):
    d = dict(
        project_monthly=report,
    )
    return render(request, 'extranet/project_monthly.html', d)


@login_required
@get_project
def home(request, project):
    d = dict(
        project_report=ProjectReport(project),
    )
    return render(request, 'extranet/base.html', d)


@login_required
@get_project
def needs(request, project):
    d = dict(
        project_report=ProjectReport(project),
        project_needs=project.need_set.all().order_by('-created_at'),
    )
    return render(request, 'extranet/project_needs.html', d)
