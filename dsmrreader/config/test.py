""" Tests with SQLite backend, which WILL result in failing some tests, but it's bloody fast. """
from dsmrreader.config.base import *


CACHES['default']['TIMEOUT'] = 0

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dsmrreader',  # Will be adjusted to 'test_*' by Django.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': '127.0.0.1',
    }
}
