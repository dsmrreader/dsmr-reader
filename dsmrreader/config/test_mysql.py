""" Tests with MySQL backend. """
from dsmrreader.config.test import *


# Use for TESTING only: GRANT ALL PRIVILEGES ON test_dsmrreader.* TO 'dsmrreader'@'localhost';
DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
