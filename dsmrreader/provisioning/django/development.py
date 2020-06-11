from dsmrreader.config.development import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
#         'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dsmrreader',
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': 'localhost',
        'CONN_MAX_AGE': 300,
    }
}

LOGGING['loggers']['commands']['level'] = 'DEBUG'
# LOGGING['loggers']['django.db'] = {
#     'handlers': ['console'],
#     'level': 'DEBUG',
# }