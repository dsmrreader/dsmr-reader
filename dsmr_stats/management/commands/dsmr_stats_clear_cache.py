from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.core.cache import cache


class Command(BaseCommand):
    help = _('Clears the cache.')

    def handle(self, **options):
        cache.clear()
