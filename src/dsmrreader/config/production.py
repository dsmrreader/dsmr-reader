from dsmrreader.config.defaults import *

print("Using PRODUCTION configuration:", __name__)

CACHES["default"]["TIMEOUT"] = 60

# Disable Django Toolbar.
MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = None
