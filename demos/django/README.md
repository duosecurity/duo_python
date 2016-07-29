Demonstration of a Django site with Duo authentication.

Tested with Django 1.10 on Python 2.7

# Setup

Install duo_app where Django can find it, for example in your PYTHONPATH.

Edit the following in settings.py:

* `DUO_IKEY` - Duo Integration Key
* `DUO_SKEY` - Duo Secret Key
* `DUO_AKEY` - Duo Applicaiton Key
* `DUO_HOST` - Duo API Host

# Test

See example_site for an example Django site which can be used to play with the
app, which has the non-Duo setup already completed, as well as the setup needed
for a complete barebones site with authorization.  To run this site:

As noted above, set up path, edit `DUO_IKEY`, `DUO_SKEY`, `DUO_AKEY`, `DUO_HOST`
in settings.py.

Start the site:

    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

Add a Django user.  The Duo user will have the same username as the
Django user; if this user does not exist, you will be able to enroll
as that user.

Now you can visit interesting URLs such as:
/private - content protected by 1fa (django) auth
/duo_private - content protected by 1fa (django) and 2fa (Duo) auth

To remove your Django and Duo authorization cookies by
visiting /accounts/logout/ & /accounts/duo_logout/, respectively.

Note that this example serves static files with the Django development server,
which is not recommended for production.
