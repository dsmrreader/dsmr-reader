from dsmrreader.config.test_postgresql import *


# https://docs.travis-ci.com/user/database-setup/#PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dsmrreader',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
}
