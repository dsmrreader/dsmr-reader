from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
import dsmr_backend.services.persistent_clients


class TestBackend(InterceptCommandStdoutMixin, TestCase):
    def setUp(self):
        self.fake_client = object()

    # from dsmr_backend.signals import initialize_persistent_client, run_persistent_client, terminate_persistent_client
    @mock.patch('dsmr_backend.signals.initialize_persistent_client.send_robust')
    def test_initialize(self, send_robust_mock):
        send_robust_mock.return_value = [
            [None, RuntimeError('Fake')],  # Error
            [None, None],  # Wrongly implemented listener
            [None, self.fake_client],  # OK
        ]

        self.assertFalse(send_robust_mock.called)
        results = dsmr_backend.services.persistent_clients.initialize()
        self.assertTrue(send_robust_mock.called)

        self.assertIn(self.fake_client, results)
        self.assertEqual(len(results), 1)  # No other results

    @mock.patch('dsmr_backend.signals.run_persistent_client.send_robust')
    def test_run(self, send_robust_mock):
        self.assertFalse(send_robust_mock.called)
        dsmr_backend.services.persistent_clients.run([self.fake_client])
        self.assertTrue(send_robust_mock.called)

        self.assertEqual(
            send_robust_mock.call_args_list[0][1]['client'],
            self.fake_client
        )

        # Test exception handling.
        send_robust_mock.return_value = [
            [None, RuntimeError('Chaos monkey happened')],
            [None, None]
        ]
        dsmr_backend.services.persistent_clients.run([self.fake_client])

    @mock.patch('dsmr_backend.signals.terminate_persistent_client.send_robust')
    def test_terminate(self, send_robust_mock):
        self.assertFalse(send_robust_mock.called)
        dsmr_backend.services.persistent_clients.terminate([self.fake_client])
        self.assertTrue(send_robust_mock.called)

        self.assertEqual(
            send_robust_mock.call_args_list[0][1]['client'],
            self.fake_client
        )

        # Test exception handling.
        send_robust_mock.return_value = [
            [None, RuntimeError('Chaos monkey happened')],
            [None, None]
        ]
        dsmr_backend.services.persistent_clients.terminate([self.fake_client])
