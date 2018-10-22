from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_backend.mixins import StopInfiniteRun


class TestCommands(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_mqtt.services.broker.initialize')
    @mock.patch('dsmr_mqtt.services.broker.run')
    @mock.patch('dsmr_mqtt.management.commands.dsmr_mqtt.Command.shutdown')
    def test_dsmr_mqtt_services(self, *mocks):
        """ Command should connect to services. """
        self.assertFalse(all([x.called for x in mocks]))
        self._intercept_command_stdout('dsmr_mqtt', run_once=True)
        self.assertTrue(all([x.called for x in mocks]))

    @mock.patch('dsmr_mqtt.services.broker.initialize')
    @mock.patch('dsmr_mqtt.services.broker.run')
    @mock.patch('dsmr_mqtt.management.commands.dsmr_mqtt.Command.shutdown')
    @mock.patch('dsmr_backend.mixins.InfiniteManagementCommandMixin._stop')
    def test_dsmr_mqtt_restart_required(self, stop_mock, shutdown_mock, *mocks):
        MQTTBrokerSettings.get_solo()
        MQTTBrokerSettings.objects.update(restart_required=True)
        self.assertFalse(shutdown_mock.called)
        self.assertFalse(stop_mock.called)

        self._intercept_command_stdout('dsmr_mqtt', run_once=True)

        self.assertTrue(shutdown_mock.called)
        self.assertTrue(stop_mock.called)

    @mock.patch('time.sleep')
    def test_dsmr_mqtt_disabled(self, sleep_mock):
        MQTTBrokerSettings.get_solo()
        MQTTBrokerSettings.objects.update(hostname=None)

        self.assertFalse(sleep_mock.called)

        with self.assertRaises(StopInfiniteRun):
            self._intercept_command_stdout('dsmr_mqtt', run_once=True)

        self.assertTrue(sleep_mock.called)

    @mock.patch('dsmr_mqtt.services.broker.initialize')
    def test_dsmr_mqtt_disabled_shutdown(self, initialize_mock):
        """ Now make sure to check the shutdown() handling. """
        initialize_mock.return_value = None

        self.assertFalse(initialize_mock.called)

        self._intercept_command_stdout('dsmr_mqtt', run_once=True)

        self.assertTrue(initialize_mock.called)

    @mock.patch('time.sleep')
    @mock.patch('paho.mqtt.client.Client.connect')
    def test_dsmr_mqtt_with_client(self, connect_mock, *mocks):
        MQTTBrokerSettings.get_solo()
        MQTTBrokerSettings.objects.update(hostname='localhost')

        self.assertFalse(connect_mock.called)

        try:
            self._intercept_command_stdout('dsmr_mqtt', run_once=True)
        except TypeError:
            # Weird mock issue.
            pass

        self.assertTrue(connect_mock.called)
