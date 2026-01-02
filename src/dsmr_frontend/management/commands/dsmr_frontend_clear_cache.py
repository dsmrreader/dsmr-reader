import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from django.core.cache import caches
from django.conf import settings


logger = logging.getLogger("dsmrreader")


class Command(BaseCommand):
    help = _("Clears the entire cache.")

    def handle(self, **options):
        for cache_key in settings.CACHES.keys():
            logger.info("Clearing cache: %s", cache_key)
            caches[cache_key].clear()

        logger.info("Done")
