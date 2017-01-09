from dsmrreader.config.production import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dsmrreader',  # Database name.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': 'localhost',
        'CONN_MAX_AGE': 60,
    }
}

# Change me when exposing your application to the outside world using the Internet!
SECRET_KEY = 'ta;<tzc;rHBVG:,|gM223ucNrz|y4,DcSK`nnWA9vBW1nXF%,8'
