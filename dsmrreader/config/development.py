import sys

from dsmrreader.config.base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dsmrreader',
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
