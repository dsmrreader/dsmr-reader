from dsmrreader.config.test.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DJANGO_DB_NAME', ''),
        'USER': os.environ.get('MYSQL_DJANGO_DB_USER', ''),
        'PASSWORD': os.environ.get('MYSQL_DJANGO_DB_PASSWORD', ''),
        'HOST': os.environ.get('MYSQL_DJANGO_DB_HOST', ''),
    }
}
