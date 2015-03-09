from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^login/$', 'extranet.views.login', name='extranet_login'),
    url(r'^$', 'extranet.views.home', name='extranet_home'),

    # === github webhook ===
    url(r'^github/webhook/(.*)/$', 'extranet.views.github.webhook',
        name='extranet_github_webhook'),

    # === coder ===
    url(r'(.+)/timer/$', 'extranet.views.coder.timer',
        name='extranet_timer'),
    url(r'^hours/(.+)/(\d+)/W(\d+)/$', 'extranet.views.coder.weekly',
        name='extranet_coder_weekly'),
    url(r'^hours/(.+)/(\d+)/(\d+)/$', 'extranet.views.coder.monthly',
        name='extranet_coder_monthly'),
    url(r'^hours/(.+)/(\d+)/(\d+)/edit/$', 'extranet.views.coder.monthly_edit',
        name='extranet_coder_monthly_edit'),
    url(r'^hours/(.+)/(\d+)/(\d+)/edit/row/$',
        'extranet.views.coder.monthly_edit_row',
        name='extranet_coder_monthly_edit_row'),
    url(r'^hours/(.+)/(\d+)/(\d+)/csv/$', 'extranet.views.coder.monthly_csv',
        name='extranet_coder_monthly_csv'),
    url(r'^hours/(.+)/$', 'extranet.views.coder.upload_hours_as_csv',
        name='extranet_upload_hours_as_csv'),

    # === team ===
    url(r'^team/(.*)/meeting/$', 'extranet.views.team.weekly_meeting',
        name='extranet_team_weekly_meeting'),

    # === customer ===
    url(r'^(.*)/(\d+)/W(\d+)/$', 'extranet.views.project.weekly',
        name='extranet_project_weekly'),
    url(r'^(.*)/(\d+)/(\d+)/$', 'extranet.views.project.monthly',
        name='extranet_project_monthly'),
    url(r'^(.*)/needs/$', 'extranet.views.project.needs', name='extranet_project_needs'),
    url(r'^(.*)/$', 'extranet.views.project.home', name='extranet_project'),

)
