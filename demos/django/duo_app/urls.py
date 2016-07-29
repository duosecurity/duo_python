from django.conf.urls import url
import duo_auth

urlpatterns = [
    url(r'^accounts/duo_login', duo_auth.login),
    url(r'^accounts/duo_logout/$', duo_auth.logout),
]
