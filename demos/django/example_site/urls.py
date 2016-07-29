from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from example_site.views import (private, public, duo_private,
    duo_private_manual, profile,
)
from django.contrib.auth.views import login, logout
import duo_app

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^private/$', private),
    url(r'^public/$', public),
    url(r'^duo_private/$', duo_private),
    url(r'^duo_private_manual/$', duo_private_manual),
    url(r'^accounts/profile/$', profile),
    url(r'^accounts/login', login),
    url(r'^accounts/logout/$', logout),
    url(r'^', include('duo_app.urls')),
]

urlpatterns += staticfiles_urlpatterns()
