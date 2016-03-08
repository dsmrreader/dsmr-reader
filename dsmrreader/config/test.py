""" Tests with SQLite backend. """
from dsmrreader.config.development import *


# Mute query debugging log for nose tests. Prevent RSI from scrolling.. ;-)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django.db.backends': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Only available (and required) for tests, so inject it here.
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('django_nose')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--cover-erase',
    '--cover-html',
    '--cover-html-dir=coverage_report/html',
]

DATABASES = {
    'default': {
        'ENGINE': None,  # Sub configs should set this.
        'NAME': 'dsmrreader',  # Will be adjusted to 'test_*' by Django.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': '127.0.0.1',
    }
}
