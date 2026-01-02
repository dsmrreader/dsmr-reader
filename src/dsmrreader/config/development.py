from dsmrreader.config.defaults import *

print("Using LOCAL DEVELOPMENT configuration:", __name__)

DEBUG = True

for k in CACHES.keys():
    CACHES[k]["TIMEOUT"] = 0

INSTALLED_APPS = list(INSTALLED_APPS)  # type: ignore
INSTALLED_APPS.append("debug_toolbar")  # type: ignore

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = "127.0.0.1"
