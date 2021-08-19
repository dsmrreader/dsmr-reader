""" Tests. """
import secrets

from dsmrreader.config.development import *


# Cache may cause weird stuff during automated testing.
for k in CACHES.keys():
    CACHES[k]['TIMEOUT'] = 0

# Never use this in production!
SECRET_KEY = secrets.token_hex(64)

# Disable caching.
for k in CACHES.keys():
    CACHES[k]['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

# Disable Django Toolbar.
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('debug_toolbar')

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = None
DSMRREADER_MAX_DATABASE_CONNECTION_SESSION_IN_SECONDS = 9999  # Never

DSMRREADER_PLUGINS = [
    'os',  # Bad example, but it works for testing anyway.
]
