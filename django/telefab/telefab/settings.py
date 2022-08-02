# This file uses the following encoding: utf-8 
# Django settings for telefab project.

from local_settings import *

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Email to send from
EMAIL_FROM = 'contact@' + WEBSITE_CONFIG['host']

# Detect if HTTPS behind a proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO","https")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Allowed website hosts
ALLOWED_HOSTS = ['*']

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = GLOBAL_ROOT + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = URL_ROOT + 'media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = GLOBAL_ROOT + 'static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = URL_ROOT + 'static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [GLOBAL_ROOT + 'templates/'],
        'OPTIONS': {
             'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
             ],
        },
    },
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
)

ROOT_URLCONF = 'telefab.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'telefab.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_cas_ng',
	'main',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': GLOBAL_ROOT + 'log/errors.log',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': GLOBAL_ROOT + 'log/debug.log',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django_cas_ng.backends': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django_cas_ng.backends': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Profile to extend the User model
AUTH_PROFILE_MODULE = "main.UserProfile"

# Website used on public computers: log out at browser close!
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Site-specific settings

# Global URL (used by CAS)
SITE_URL = WEBSITE_CONFIG['protocol'] + "://" + WEBSITE_CONFIG['host']

# URL to log in
LOGIN_URL = URL_ROOT + 'connexion'

# Path to redirect to on successful login.
LOGIN_REDIRECT_URL = URL_ROOT

# Path to redirect to on unsuccessful login attempt.
LOGIN_REDIRECT_URL_FAILURE = URL_ROOT + "connexion"

# URL of the Telecom Bretagne CAS server
CAS_SERVER_URL = "https://login.telecom-bretagne.eu/cas/"

# Create users in database automatically
CAS_CREATE_USERS = True

# Global URL (used by CAS)
CAS_RESIRECT_URL = WEBSITE_CONFIG['protocol'] + "://" + WEBSITE_CONFIG['host'] + WEBSITE_CONFIG['path']

# References to data in the DB (to create before running the website!)
ANIMATORS_GROUP_NAME = u"Animateurs"
MAIN_PLACE_NAME = u"Téléfab Brest"