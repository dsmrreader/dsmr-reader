""" Tests with MySQL backend. """
from dsmrreader.config.test import *


# Use for TESTING only:
#   mysqladmin create test_dsmrtest
#   GRANT ALL PRIVILEGES ON test_dsmrreader.* TO 'dsmrreader'@'localhost';
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dsmrtest',  # Will be prefixed with 'test_' by Django.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': '127.0.0.1',
    }
}
