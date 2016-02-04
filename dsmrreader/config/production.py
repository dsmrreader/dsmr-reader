"""
Production configs should not be committed into version control.
However, since this project is localhost only, I do not care ;-)
"""

from dsmrreader.config.development import *

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = None  # Please use one of the prepared configs per database backend.

STATIC_ROOT = '/var/www/dsmrreader/static'

CACHES['default']['TIMEOUT'] = 1 * 60
