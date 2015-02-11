# django
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# extranet
from extranet.models import Project, ProjectReport, MonthlyReport


# === utils ===

def get_customer_project_and_month(func):
    def wrapper(request, project_name, year=None, month=None):
        project = get_object_or_404(Project, name=project_name)
        if (
                not request.user.is_superuser
                and not request.user in project.customer_team.user_set.all()
        ):
            raise Http404()
        year = int(year) if year else None
        month = int(month) if month else None
        return func(request, project, year, month)
    return wrapper


# === views ===

@login_required
@get_customer_project_and_month
def monthly_report(request, project, year, month):
    report = ProjectReport(project)
    d = dict(
        project_report=report,
        monthly_report=(
            MonthlyReport(project, year, month) if (year and month) else None
        ),
    )
    return render(request, 'extranet/monthly_report.html', d)
