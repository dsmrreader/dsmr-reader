"""
Production configs should not be committed into version control.
However, since this project is localhost only, I do not care ;-)
"""

from dsmrreader.config.development import *

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
### Choose either MySQL/MariaDB or PostgreSQL. 
### SQLite should work as well, but is untested!
#        'ENGINE': 'django.db.backends.mysql',
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dsmrreader',
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'CONN_MAX_AGE': 300,
    }
}

STATIC_ROOT = '/var/www/dsmrreader/static'

CACHES['default']['TIMEOUT'] = 5 * 60
