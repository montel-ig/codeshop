# python
from datetime import date

# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
    year, week = date.today().isocalendar()[:2]
    d = dict(
        code_projects=projects,
        teams=teams,
        year=year,
        week=week,
    )
    return render(request, 'extranet/home.html', d)
