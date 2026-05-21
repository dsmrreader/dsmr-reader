from unittest import mock

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from django.test import TestCase


class TestDsmrStatsClearCache(InterceptCommandStdoutMixin, TestCase):
    """Tests whether manually clearing the cache works."""

    @mock.patch("dsmr_frontend.management.commands.dsmr_frontend_clear_cache.caches")
    def test(self, mock_caches):
        """Test dsmr_frontend_clear_cache deprecation and fallback."""
        mock_cache = mock.MagicMock()
        mock_caches.__getitem__.return_value = mock_cache
        self._intercept_command_stdout("dsmr_frontend_clear_cache")
        self.assertTrue(mock_cache.clear.called)
