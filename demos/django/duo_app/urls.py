from django.conf.urls import patterns
import duo_auth

urlpatterns = patterns(
    '',
    (r'accounts/duo_login/$', duo_auth.login),
    (r'accounts/duo_logout/$', duo_auth.logout))
