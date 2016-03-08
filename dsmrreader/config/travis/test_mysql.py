from dsmrreader.config.test import *


# https://docs.travis-ci.com/user/database-setup/#MySQL
DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
DATABASES['default']['USER'] = 'travis'
DATABASES['default']['PASSWORD'] = ''
