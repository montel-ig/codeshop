from django.conf import settings
 
 
def global_settings(request):
    return dict(
        (key, getattr(settings, key))
        for key in ['SITE_NAME']
    )


def user_projects_and_teams(request):
    # TODO: it'd be nicer to create our own User model so we wouldn't need this
    projects = set()
    teams = set()
    for group in request.user.groups.all():
        projects.update(group.code_projects.all())
        if group.customer_projects.all():
            teams.add(group)
    return dict(
        projects_for_customers=projects,
        teams_for_coders=teams,
    )
