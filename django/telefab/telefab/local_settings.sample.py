# Django local settings (per-server)

# Debug mode?
DEBUG = True

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'telefab-website',                      # Or path to database file if using sqlite3.
        'USER': 'telefab-website',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Django apps root directory
GLOBAL_ROOT = '/home/tristan/Developpement/Web/telefab-website/django/'

# Site root URL
URL_ROOT = '/lab/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ob#3jske&amp;-p0%5h%!z=bywt*$sl3euh=*soix0vmzn798vbn_('
