"""
Production configs should not be committed into version control.
However, since this project is localhost only, I do not care ;-)
"""

from dsmrreader.config.base import *


DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = None  # Please use one of the prepared configs for your database backend.

STATIC_ROOT = '/var/www/dsmrreader/static'

CACHES['default']['TIMEOUT'] = 1 * 60


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s @ %(module)s | %(message)s'
        },
    },
    'handlers': {
        'django_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'logs', 'django.log'),
            'formatter': 'verbose',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB max.
            'backupCount': 7,
        },
        'dsmrreader_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'logs', 'dsmrreader.log'),
            'formatter': 'verbose',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB max.
            'backupCount': 7,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'dsmrreader': {
            'handlers': ['dsmrreader_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# Disable Django Toolbar.
MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = None
