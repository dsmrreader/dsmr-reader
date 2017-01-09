""" Tests with SQLite backend. """
from dsmrreader.config.development import *


# Mute query debugging log for nose tests. Prevent RSI from scrolling.. ;-)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django.db.backends': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# Disable DDT.
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove('debug_toolbar')

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
MIDDLEWARE_CLASSES.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = None
