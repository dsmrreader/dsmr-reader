from dsmrreader.config.base import *


DEBUG = True
CACHES['default']['TIMEOUT'] = 0

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            # logging handler that outputs log messages to terminal
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',  # message level to be written to console
        },
    },
    'loggers': {
        'django.db.backends': {
#            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'dsmrreader': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('debug_toolbar')

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = '127.0.0.1'

ALLOWED_HOSTS = ['*']
