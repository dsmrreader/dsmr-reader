import os

from dsmrreader.config.production import *


# Default settings, adjust if you use other ones, or use environment variables.
DSMRREADER_NAME = 'dsmrreader'
DSMRREADER_USER = 'dsmrreader'
DSMRREADER_PASSWORD = 'dsmrreader'
DSMRREADER_HOST = 'localhost'
DSMRREADER_PORT = 3306
DSMRREADER_CONN_MAX_AGE = 60

# Change me when exposing your application to the outside world using the Internet!
DSMRREADER_SECRET_KEY = 'Ww\=)|a:tKxz"u@p<<Cp~MaZ%dNIYX-#w2h-*Od{>1`c%l/MJ+'


# Settings are read from environment or, when not found, default to the values above.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', DSMRREADER_NAME),
        'USER': os.environ.get('DB_USER', DSMRREADER_USER),
        'PASSWORD': os.environ.get('DB_PASS', DSMRREADER_PASSWORD),
        'HOST': os.environ.get('DB_HOST', DSMRREADER_HOST),
        'PORT': os.environ.get('DB_PORT', DSMRREADER_PORT),        
        'CONN_MAX_AGE': os.environ.get('CONN_MAX_AGE', DSMRREADER_CONN_MAX_AGE),
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY', DSMRREADER_SECRET_KEY)

if os.environ.get('DSMRREADER_LOGLEVEL') is not None:
    LOGGING['loggers']['commands']['level'] = os.environ.get('DSMRREADER_LOGLEVEL')

"""
    Enable and change the logging level below to alter the verbosity of the (backend) command(s).
    - DEBUG:             Log everything.
    - INFO:              Log most things.
    - WARNING (default): Log only warnings and errors.

    Restart the commands in Supervisor to apply any changes.
"""
# LOGGING['loggers']['commands']['level'] = 'DEBUG'
