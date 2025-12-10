"""Tests."""

import secrets

from dsmrreader.config.development import *

print("Using AUTOMATED TESTS configuration:", __name__)

# Cache may cause weird stuff during automated testing.
for k in CACHES.keys():
    CACHES[k]["TIMEOUT"] = 0

# Never use this in production!
SECRET_KEY = secrets.token_hex(64)

# Disable caching.
for k in CACHES.keys():
    CACHES[k]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"

# Disable Django Toolbar.
INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.remove("debug_toolbar")

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = None
DSMRREADER_MAX_DATABASE_CONNECTION_SESSION_IN_SECONDS = 9999  # Never

DSMRREADER_PLUGINS = [
    "os",  # Bad example, but it works for testing anyway.
]

# When defined, just use these.
try:
    DATABASES["default"]["HOST"] = config("TEST_DJANGO_DATABASE_HOST", cast=str)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["PORT"] = config("TEST_DJANGO_DATABASE_PORT", cast=int)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["NAME"] = config("TEST_DJANGO_DATABASE_NAME", cast=str)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["USER"] = config("TEST_DJANGO_DATABASE_USER", cast=str)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["PASSWORD"] = config("TEST_DJANGO_DATABASE_PASSWORD", cast=str)
except UndefinedValueError:
    pass
