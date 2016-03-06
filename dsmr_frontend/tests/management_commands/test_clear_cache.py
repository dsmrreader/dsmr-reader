from time import sleep

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from django.core.cache import cache
from django.test import TestCase


class TestDsmrStatsClearCache(InterceptStdoutMixin, TestCase):
    """ Tests whether manually clearing the cache works. """
    def test(self):
        """ Test dsmr_frontend_clear_cache deprecation and fallback. """
        CACHE_KEY = "12345-test"
        CACHE_VALUE = "All your caches belong to us"

        cache.clear()
        self.assertIsNone(cache.get(CACHE_KEY))

        cache.set(CACHE_KEY, CACHE_VALUE, 9999)
        sleep(1)

        self.assertEqual(cache.get(CACHE_KEY), CACHE_VALUE)

        self._intercept_command_stdout('dsmr_frontend_clear_cache')
        self.assertIsNone(cache.get(CACHE_KEY))
