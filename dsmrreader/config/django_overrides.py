"""
    Django settings overrided from env.
    Mostly try-except because we don't want to pin any defaults to fallback to, just let Django set them.
"""
from decouple import config, UndefinedValueError


# Not all database engines require the full config.
DATABASES = {
    'default': {
        'ENGINE': config(
            'DB_ENGINE',  # @deprecated v4.5, removed v5.0
            default=config('DJANGO_DATABASE_ENGINE', cast=str, default=None)  # Do no longer fallback to NONE in v5.0!
        ),
        'CONN_MAX_AGE': config(
            'CONN_MAX_AGE',  # @deprecated v4.5, removed v5.0
            default=config('DJANGO_DATABASE_CONN_MAX_AGE', cast=int, default=60),
            cast=int
        ),
    }
}

try:
    DATABASES['default']['HOST'] = config(
        'DB_HOST',  # @deprecated v4.5, removed v5.0
        default=config('DJANGO_DATABASE_HOST', cast=str, default=None)  # Do no longer fallback to NONE in v5.0!
    )
except UndefinedValueError:
    pass

try:
    DATABASES['default']['PORT'] = config(
        'DB_PORT',  # @deprecated v4.5, removed v5.0
        default=config('DJANGO_DATABASE_PORT', cast=int, default=0),  # Do no longer fallback to 0 in v5.0!
        cast=int
    )
except UndefinedValueError:
    pass

try:
    DATABASES['default']['NAME'] = config(
        'DB_NAME',  # @deprecated v4.5, removed v5.0
        default=config('DJANGO_DATABASE_NAME', cast=str, default=None)  # Do no longer fallback to NONE in v5.0!
    )
except UndefinedValueError:
    pass

try:
    DATABASES['default']['USER'] = config(
        'DB_USER',  # @deprecated v4.5, removed v5.0
        default=config('DJANGO_DATABASE_USER', cast=str, default=None)  # Do no longer fallback to NONE in v5.0!
    )
except UndefinedValueError:
    pass

try:
    DATABASES['default']['PASSWORD'] = config(
        'DB_PASS',  # @deprecated v4.5, removed v5.0
        default=config('DJANGO_DATABASE_PASSWORD', cast=str, default=None)  # Do no longer fallback to NONE in v5.0!
    )
except UndefinedValueError:
    pass


SECRET_KEY = config(
    'SECRET_KEY',  # @deprecated v4.5, removed v5.0
    default=config('DJANGO_SECRET_KEY', cast=str, default=None)  # Do no longer fallback to NONE in v5.0!
)

TIME_ZONE = config('DJANGO_TIME_ZONE', cast=str, default='Europe/Amsterdam')

if not TIME_ZONE:  # Default()-ception does not work for some reason.
    # @deprecated v4.5, removed v5.0
    TIME_ZONE = config('TZ', cast=str, default=TIME_ZONE)

try:
    STATIC_URL = config('DJANGO_STATIC_URL', cast=str)
except UndefinedValueError:
    pass

try:
    FORCE_SCRIPT_NAME = config('DJANGO_FORCE_SCRIPT_NAME', cast=str)
except UndefinedValueError:
    pass

try:
    USE_X_FORWARDED_HOST = config('DJANGO_USE_X_FORWARDED_HOST', cast=bool)
except UndefinedValueError:
    pass

try:
    USE_X_FORWARDED_PORT = config('DJANGO_USE_X_FORWARDED_PORT', cast=bool)
except UndefinedValueError:
    pass

try:
    X_FRAME_OPTIONS = config('DJANGO_X_FRAME_OPTIONS', cast=str)
except UndefinedValueError:
    pass

try:
    STATIC_ROOT = config('DJANGO_STATIC_ROOT', cast=str)
except UndefinedValueError:
    pass
