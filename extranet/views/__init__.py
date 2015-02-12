# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# extranet
from extranet.models import CoderReport


# === utils ===

def login(request):
    return render(request, 'extranet/login.html')


# === views ===

@login_required
def home(request):
    projects = set()
    teams = set()
    for group in request.user.groups.all():
        projects.update(group.code_projects.all())
        if group.customer_projects.all():
            teams.add(group)

    d = dict(
        code_projects=projects,
        teams=teams,
        coder_report=CoderReport(request.user) if teams else None,
    )
    return render(request, 'extranet/home.html', d)
