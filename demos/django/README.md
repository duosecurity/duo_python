Demonstration of a Django site with Duo authentication.

Developed with Django 1.2.  Requires django.contrib.auth.

# Setup

Install duo_app where Django can find it, for example in your PYTHONPATH.

Edit the following in settings.py:

* `DUO_LOGIN_URL` - URL to use for Duo authentication redirects.  This
can be any unique URL, `/accounts/duo_login` matches the Django
authentication URL.
* `DUO_IKEY`, `DUO_SKEY`, `DUO_AKEY`, DUO_HOST` - Appropriate Duo keys and API host.
* `STATIC_PREFIX` - Prefix for URLs where static files are served
from, without the trailing slash (e.g. '/static',
'http://example.com/static')
* `INSTALLED_APPS` - should contain 'duo_app'

Copy duo_app/static/Duo-Web-v1.bundled.min.js to wherever you're serving static
files from.

# Test

See example_site for an example Django site which can be used to play with the
app, which has the non-Duo setup already completed, as well as the setup needed
for a complete barebones site with authorization.  To run this site:

As noted above, set up path, edit `DUO_IKEY`, `DUO_SKEY`, `DUO_AKEY`, `DUO_HOST`
in settings.py, and copy Duo-Web-v1.bundled.min.js to the static directory.

Start the site:

    python manage.py syncdb; python manage.py runserver

Add a Django user.  The Duo user will have the same username as the
Django user; if this user does not exist, you will be able to enroll
as that user.

Now you can visit interesting URLs such as /public, /private, /duo_private,
and /duo_private_manual.  To remove your Django and Duo authorization cookies,
visit /accounts/duo_logout and /accounts/logout.

Note that this example serves static files with the Django development server,
which is not recommended for production.
