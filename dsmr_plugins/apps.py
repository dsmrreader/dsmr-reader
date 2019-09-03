import importlib

from django.apps import AppConfig
from django.conf import settings


class PluginsAppConfig(AppConfig):
    name = 'dsmr_plugins'

    def ready(self):
        # Required due to error: "SyntaxError: import * only allowed at module level"
        for current in settings.DSMRREADER_PLUGINS:
            importlib.import_module(current)
