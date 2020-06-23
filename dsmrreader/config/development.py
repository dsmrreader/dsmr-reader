from dsmrreader.config.defaults import *


DEBUG = True

for k in CACHES.keys():
    CACHES[k]['TIMEOUT'] = 0

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('debug_toolbar')

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = '127.0.0.1'
