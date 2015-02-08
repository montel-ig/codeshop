from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^login/$', 'extranet.views.login', name='extranet_login'),

    url(r'^$', 'extranet.views.home', name='extranet_home'),

    url(r'^hours/$', 'extranet.views.hours', name='extranet_hours'),

    # url(r'^overview/$', 'extranet.views.overview', name='extranet_overview'),
    # url(r'^overview/data.json$', 'extranet.views.overview_json'),
)
