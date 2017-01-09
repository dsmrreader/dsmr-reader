from dsmrreader.config.production import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dsmrreader',  # Database name.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': 'localhost',
        'CONN_MAX_AGE': 60,
    }
}

# Change me when exposing your application to the outside world using the Internet!
SECRET_KEY = 'aUqm$#!1yIILyt3^hDDy`Fv!&%kM>aI&#H(}a0JV~fec;rS%tH'
