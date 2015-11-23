"""
Production configs should not be committed into version control.
However, since this project is localhost only, I do not care ;-)
"""

from dsmrreader.config.development import *

DEBUG = False
ALLOWED_HOSTS = ['*']

# DATABASES = Copied from development.

STATIC_ROOT = '/var/www/dsmrreader/static'

CACHES['default']['TIMEOUT'] = 5 * 60
