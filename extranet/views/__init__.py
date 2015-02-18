# django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# extranet
from extranet.models import CoderReport, Coder


# === utils ===

def login(request):
    return render(request, 'extranet/login.html', {'next': request.GET.get('next', '/')})


# === views ===

@login_required
def home(request):
    coder = Coder.get_or_none(username=request.user.username)

    projects = set()
    for group in request.user.groups.all():
        projects.update(group.code_projects.all())

    d = dict(
        coder=coder,
        code_projects=projects,
        coder_report=CoderReport(coder) if coder else None,
    )
    return render(request, 'extranet/home.html', d)
