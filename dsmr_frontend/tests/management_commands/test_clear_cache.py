from unittest import mock

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from django.test import TestCase


class TestDsmrStatsClearCache(InterceptCommandStdoutMixin, TestCase):
    """ Tests whether manually clearing the cache works. """
    @mock.patch('django.core.cache.backends.dummy.DummyCache.clear')
    def test(self, cache_mock):
        """ Test dsmr_frontend_clear_cache deprecation and fallback. """
        self._intercept_command_stdout('dsmr_frontend_clear_cache')
        self.assertTrue(cache_mock.called)
