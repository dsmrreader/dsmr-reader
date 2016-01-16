from time import sleep

from django.core.management import call_command
from django.core.cache import cache
from django.test import TestCase


class TestDsmrStatsClearCache(TestCase):
    """ Tests whether manually clearing the cache works. """
    def test(self):
        """ Test dsmr_stats_datalogger deprecation and fallback. """
        CACHE_KEY = "12345-test"
        CACHE_VALUE = "All your caches belong to us"

        cache.clear()
        self.assertIsNone(cache.get(CACHE_KEY))

        cache.set(CACHE_KEY, CACHE_VALUE, 9999)
        sleep(1)

        self.assertEqual(cache.get(CACHE_KEY), CACHE_VALUE)

        call_command('dsmr_stats_clear_cache')
        self.assertIsNone(cache.get(CACHE_KEY))
