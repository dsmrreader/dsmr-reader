from unittest import mock

from django.test import TestCase
from paho.mqtt.client import Client

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_backend.signals import initialize_persistent_client, run_persistent_client, terminate_persistent_client


class TestCases(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_mqtt.services.broker.initialize_client')
    def test_initialize_persistent_client_signal(self, initialize_mock):
        initialize_mock.return_value = None

        self.assertFalse(initialize_mock.called)
        initialize_persistent_client.send_robust(None)
        self.assertTrue(initialize_mock.called)

    @mock.patch('dsmr_mqtt.services.broker.run')
    def test_run_persistent_client_signal(self, run_mock):
        run_mock.return_value = None

        self.assertFalse(run_mock.called)
        run_persistent_client.send_robust(None, client=None)  # Invalid client.
        self.assertFalse(run_mock.called)

        mqtt_client = Client()

        self.assertFalse(run_mock.called)
        run_persistent_client.send_robust(None, client=mqtt_client)
        self.assertTrue(run_mock.called)

    @mock.patch('paho.mqtt.client.Client.disconnect')
    def test_terminate_persistent_client(self, disconnect_mock):
        mqtt_client = Client()

        self.assertFalse(disconnect_mock.called)
        terminate_persistent_client.send_robust(None, client=mqtt_client)
        self.assertTrue(disconnect_mock.called)
