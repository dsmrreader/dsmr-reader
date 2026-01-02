"""
Django settings overwritten from env.
Mostly try-except because we don't want to pin any defaults to fall back to, just let Django set them.
"""

from decouple import config, UndefinedValueError, Csv

# Not all database engines require the full config.
DATABASES = {
    "default": {
        "ENGINE": config("DJANGO_DATABASE_ENGINE", cast=str),
        "CONN_MAX_AGE": config("DJANGO_DATABASE_CONN_MAX_AGE", cast=int, default=60),
    }
}

try:
    DATABASES["default"]["HOST"] = config("DJANGO_DATABASE_HOST", cast=str)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["PORT"] = config("DJANGO_DATABASE_PORT", cast=int)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["NAME"] = config("DJANGO_DATABASE_NAME", cast=str)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["USER"] = config("DJANGO_DATABASE_USER", cast=str)
except UndefinedValueError:
    pass

try:
    DATABASES["default"]["PASSWORD"] = config("DJANGO_DATABASE_PASSWORD", cast=str)
except UndefinedValueError:
    pass


SECRET_KEY = config("DJANGO_SECRET_KEY", cast=str)
TIME_ZONE = config("DJANGO_TIME_ZONE", cast=str, default="Europe/Amsterdam")

try:
    ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", cast=Csv(post_process=list))
except UndefinedValueError:
    pass

try:
    STATIC_URL = config("DJANGO_STATIC_URL", cast=str)
except UndefinedValueError:
    pass

try:
    FORCE_SCRIPT_NAME = config("DJANGO_FORCE_SCRIPT_NAME", cast=str)
except UndefinedValueError:
    pass

try:
    USE_X_FORWARDED_HOST = config("DJANGO_USE_X_FORWARDED_HOST", cast=bool)
except UndefinedValueError:
    pass

try:
    USE_X_FORWARDED_PORT = config("DJANGO_USE_X_FORWARDED_PORT", cast=bool)
except UndefinedValueError:
    pass

try:
    X_FRAME_OPTIONS = config("DJANGO_X_FRAME_OPTIONS", cast=str)
except UndefinedValueError:
    pass

try:
    STATIC_ROOT = config("DJANGO_STATIC_ROOT", cast=str)
except UndefinedValueError:
    pass

try:
    CSRF_COOKIE_AGE = config("DJANGO_CSRF_COOKIE_AGE", cast=int)
except UndefinedValueError:
    pass

try:
    CSRF_COOKIE_DOMAIN = config("DJANGO_CSRF_COOKIE_DOMAIN", cast=str)
except UndefinedValueError:
    pass

try:
    CSRF_COOKIE_HTTPONLY = config("DJANGO_CSRF_COOKIE_HTTPONLY", cast=bool)
except UndefinedValueError:
    pass

try:
    CSRF_COOKIE_NAME = config("DJANGO_CSRF_COOKIE_NAME", cast=str)
except UndefinedValueError:
    pass

try:
    CSRF_COOKIE_PATH = config("DJANGO_CSRF_COOKIE_PATH", cast=str)
except UndefinedValueError:
    pass

try:
    CSRF_COOKIE_SAMESITE = config("DJANGO_CSRF_COOKIE_SAMESITE", cast=str)
except UndefinedValueError:
    pass
try:
    CSRF_COOKIE_SECURE = config("DJANGO_CSRF_COOKIE_SECURE", cast=bool)
except UndefinedValueError:
    pass

try:
    CSRF_USE_SESSIONS = config("DJANGO_CSRF_USE_SESSIONS", cast=bool)
except UndefinedValueError:
    pass

try:
    CSRF_HEADER_NAME = config("DJANGO_CSRF_HEADER_NAME", cast=str)
except UndefinedValueError:
    pass

try:
    CSRF_TRUSTED_ORIGINS = config("DJANGO_CSRF_TRUSTED_ORIGINS", cast=Csv(post_process=list))
except UndefinedValueError:
    pass
