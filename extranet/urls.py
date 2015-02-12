from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^login/$', 'extranet.views.login', name='extranet_login'),
    url(r'^$', 'extranet.views.home', name='extranet_home'),

    # === coder ===
    url(r'^hours/(.+)/(\d+)/W(\d+)/$', 'extranet.views.coder.weekly_hours',
        name='extranet_weekly_hours'),
    url(r'^hours/(.+)/(\d+)/(\d+)/$', 'extranet.views.coder.monthly_hours',
        name='extranet_monthly_hours'),
    url(r'^hours/(.+)/$', 'extranet.views.coder.upload_hours_as_csv',
        name='extranet_upload_hours_as_csv'),
    url(r'^hours/$', 'extranet.views.coder.upload_hours_as_csv',
        name='extranet_upload_hours_as_csv'),

    # === customer ===
    url(r'^(.*)/(\d+)-(\d\d)/$', 'extranet.views.customer.monthly_report',
        name='extranet_monthly_report'),
    url(r'^(.*)/$', 'extranet.views.customer.monthly_report',
        name='extranet_monthly_report'),
)
