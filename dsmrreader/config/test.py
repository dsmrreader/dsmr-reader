""" Tests with SQLite backend. """
from dsmrreader.config.development import *


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
        # SQLite is NOT supported, but might work, so experimental!
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'dsmrreader',  # Will be adjusted to 'test_*' by Django.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': '127.0.0.1',
    }
}
