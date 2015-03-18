from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^private/$', 'example_site.views.private'),
    url(r'^public/$', 'example_site.views.public'),
    url(r'^duo_private/$', 'example_site.views.duo_private'),
    url(r'^duo_private_manual/$', 'example_site.views.duo_private_manual'),
    url(r'^accounts/profile/$', 'example_site.views.profile'),
    url(r'^accounts/login/$',  'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^', include('duo_app.urls')),
)

urlpatterns += staticfiles_urlpatterns()
