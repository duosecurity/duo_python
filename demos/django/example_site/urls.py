from django.conf.urls.defaults import *
import settings

import duo_app.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Prefix for static URLs, suitable for urlpatterns.  This is a hassle because
# STATIC_PREFIX should work for prefixing the URL in a template whether it's
# local or absolute.  We're using a local one here, but urlpatterns doesn't
# want a leading slash.
static_url_prefix = settings.STATIC_PREFIX[1:]

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    # URLs which demonstrate the use of authorization
    (r'^private/$', 'views.private'),
    (r'^public/$', 'views.public'),
    (r'^duo_private/$', 'views.duo_private'),
    (r'^duo_private_manual/$', 'views.duo_private_manual'),
    # URLs required by django.contrib.auth
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/profile/$', 'views.profile'),
    # Serve static files from /static/.
    # This is served insecurely for demonstration purposes.  Should
    # use a webserver for this in production, or see django 1.3.
    (r'^%s/(?P<path>.*)$' % static_url_prefix, 'django.views.static.serve',
     {'document_root': settings.STATIC_DIRECTORY}))

urlpatterns += duo_app.urls.urlpatterns
