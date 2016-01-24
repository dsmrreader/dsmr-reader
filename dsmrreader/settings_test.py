from dsmrreader.config.base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

CACHES['default']['TIMEOUT'] = 0
