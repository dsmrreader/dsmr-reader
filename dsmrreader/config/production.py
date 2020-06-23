from dsmrreader.config.defaults import *


CACHES['default']['TIMEOUT'] = 60

STATIC_ROOT = '/var/www/dsmrreader/static'

# Disable Django Toolbar.
MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = None
