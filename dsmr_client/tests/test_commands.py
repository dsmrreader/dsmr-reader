from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin


class TestCommands(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_mqtt.services.broker.initialize')
    @mock.patch('dsmr_mqtt.services.broker.run')
    @mock.patch('dsmr_client.management.commands.dsmr_client.Command.shutdown')
    def test_dsmr_client_services(self, *mocks):
        """ Command should connect to services. """
        self.assertFalse(all([x.called for x in mocks]))
        self._intercept_command_stdout('dsmr_client', run_once=True)
        self.assertTrue(all([x.called for x in mocks]))
