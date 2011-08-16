# Django settings for example_site project.

# Root directory for this installation as a string, so we don't have to
# hardcode the paths.  This assumes that the app is installed here.
# This is for demonstration purposes and could probably be broken when
# distributed as an egg or whatever.
import os
BASE_DIR = os.path.dirname(os.path.normpath(__file__))

# URL for Django local login form.
LOGIN_URL = '/accounts/login'
# URL for Duo login form.  This is here to match the Django URLs; change
# how the Duo URLs are included to move this.
DUO_LOGIN_URL = '/accounts/duo_login'

# Static file serving.  Duo requires that STATIC_PREFIX contains the URL
# prefix for where its Javascript file will be served from, the rest is 
# specific to your installation.
# Absolute URL prefix for where static files are served from.
# Do not include the trailing slash.
STATIC_PREFIX = '/static'
# Local directory where static files are served from.
# Include the leading slash, do not include the trailing slash.
STATIC_DIRECTORY = '/'.join([BASE_DIR, 'static'])

# Duo configuration.
DUO_IKEY = ''
DUO_SKEY = ''
DUO_AKEY = ''
DUO_HOST = ''

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',    
    'duo_app')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/'.join([BASE_DIR, 'sqlite.db']),
    }
}

TEMPLATE_DIRS = (
    '/'.join([BASE_DIR, 'templates']),)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6#jhv1%cj)!4ajbw8c&-=v!d3x*elcp$let02zh&n!rs4d**%j'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'example_site.urls'
