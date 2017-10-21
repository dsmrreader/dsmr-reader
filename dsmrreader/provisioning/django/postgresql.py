import os
from dsmrreader.config.production import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'dsmrreader'),
        'USER': os.environ.get('DB_USER', 'dsmrreader'),
        'PASSWORD': os.environ.get('DB_PASS', 'dsmrreader'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'CONN_MAX_AGE': os.environ.get('CONN_MAX_AGE', 60),
    }
}

# Change me when exposing your application to the outside world using the Internet!
SECRET_KEY = os.environ.get('SECRET_KEY', 'ta;<tzc;rHBVG:,|gM223ucNrz|y4,DcSK`nnWA9vBW1nXF%,8')
