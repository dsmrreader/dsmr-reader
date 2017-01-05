from dsmrreader.config.test.mysql import *


# https://docs.travis-ci.com/user/database-setup/#MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dsmrreader',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
    }
}
