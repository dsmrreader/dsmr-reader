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
    },
}
