from dsmrreader.config.test.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PSQL_DJANGO_DB_NAME', ''),
        'USER': os.environ.get('PSQL_DJANGO_DB_USER', ''),
        'HOST': os.environ.get('PSQL_DJANGO_DB_HOST', ''),
    }
}
