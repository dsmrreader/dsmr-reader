from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.core.cache import caches
from django.conf import settings


class Command(BaseCommand):
    help = _('Clears the entire cache.')

    def handle(self, **options):
        for cache_key in settings.CACHES.keys():
            self.stdout.write('Clearing cache: {}'.format(cache_key))
            caches[cache_key].clear()

        self.stdout.write('Done')
