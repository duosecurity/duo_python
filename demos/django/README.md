Demonstration of a Django site with Duo authentication.

Tested with Django 1.10 on Python 2.7 and Python 3.5.

`example_site` is an example Django site which can be used to play with the
app, which has the non-Duo setup already completed, as well as the setup needed
for a complete barebones site with authorization. 

# Setup

* Set up a virtualenv*

Create a virtualenv and install dependencies:

```
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

* Add Duo configuration *

Edit the following in settings.py:

* `DUO_IKEY` - Duo Integration Key
* `DUO_SKEY` - Duo Secret Key
* `DUO_AKEY` - Duo Application Key
* `DUO_HOST` - Duo API Host

* Set up Django:*

At the terminal run the initial database migrations:

```
python manage.py makemigrations
python manage.py migrate
```

Open up the Python REPL with `python` and add a user:

```
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_site.settings")
import django
django.setup()
from django.contrib.auth.models import User
user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
```


*Start the site*

    python manage.py runserver


After starting the server, you can browse to `http://127.0.0.1:8000`. 

The username (from the user you added above) is `john` and password is `johnpassword`.

You can now check out paths like:
`/private` - content protected by 1fa (django) auth. 
/duo_private - content protected by 1fa (django) and 2fa (Duo) auth

To remove your Django and Duo authorization cookies by
visiting /accounts/logout/ & /accounts/duo_logout/, respectively.

Note that this example serves static files with the Django development server,
which is not recommended for production.
