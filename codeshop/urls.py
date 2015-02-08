from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    # === admin ===
    url(r'^admin/', include(admin.site.urls)),

    # === social auth ===
    url(r'', include('social_auth.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='logout'),

    # === extranet ===
    url(r'', include('extranet.urls')),
)
