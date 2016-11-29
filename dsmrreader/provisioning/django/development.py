from dsmrreader.config.development import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
#         'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dsmrreader',  # Database name.
        'USER': 'dsmrreader',
        'PASSWORD': 'dsmrreader',
        'HOST': 'localhost',
        'CONN_MAX_AGE': 300,
    }
}


# # Sentry integration.
# import raven
#
# INSTALLED_APPS = list(INSTALLED_APPS)
# INSTALLED_APPS.append('raven.contrib.django.raven_compat')
#
# RAVEN_CONFIG = {
#     'dsn': 'http://XXXXX:YYYYY@HOST:PORT/ZZZZZ',
#     # If you are using git, you can also automatically configure the
#     # release based on the git info.
#     'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
# }
