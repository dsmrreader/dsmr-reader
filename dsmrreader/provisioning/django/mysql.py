from dsmrreader.config.production import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dsmrreader',  # Database name.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': 'localhost',
        'CONN_MAX_AGE': 300,
    }
}
