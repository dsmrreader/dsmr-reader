""" Tests with SQLite backend. """
from dsmrreader.config.development import *


DATABASES = {
    'default': {
        # SQLite is NOT supported and will FAIL tests. Use only for developing tests initially.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dsmrreader',  # Will be adjusted to 'test_*' by Django.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': '127.0.0.1',
    }
}
