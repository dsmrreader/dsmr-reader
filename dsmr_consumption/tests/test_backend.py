from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin


class TestBackend(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_consumption.services.compact_all')
    def test_services_called(self, *mocks):
        """ Test whether services are called. """
        for current in mocks:
            self.assertFalse(current.called)

        self._intercept_command_stdout('dsmr_backend', run_once=True)

        for current in mocks:
            self.assertTrue(current.called)
