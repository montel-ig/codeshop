# django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# extranet
from extranet.models import TeamWeeklyMeeting


# === utils ===

def get_team(func):
    def wrapper(request, team_name, *args, **kwargs):
        team = get_object_or_404(Group, name=team_name)
        if (
                not request.user.is_superuser
                and not request.user in team.user_set.all()
        ):
            raise Http404()
        return func(request, team, *args, **kwargs)
    return wrapper


# === views ===

@login_required
@get_team
def weekly_meeting(request, team):
    d = dict(
        team_weekly_meeting=TeamWeeklyMeeting(team),
    )
    return render(request, 'extranet/team_weekly_meeting.html', d)
