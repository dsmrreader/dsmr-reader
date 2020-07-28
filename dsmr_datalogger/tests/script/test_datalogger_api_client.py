"""
This only tests the __main__ route and methods not covered by other tests.
"""
from unittest import mock
import logging

from django.test import TestCase
import requests
import serial

import dsmr_datalogger.scripts.dsmr_datalogger_api_client


@mock.patch('time.sleep')
@mock.patch.dict('os.environ', dict(
    DATALOGGER_INPUT_METHOD='serial',
    DATALOGGER_SERIAL_PORT='/dev/X',
    DATALOGGER_SERIAL_BAUDRATE='12345',
    DATALOGGER_API_HOSTS='https://127.0.0.1:1234',
    DATALOGGER_API_KEYS='test-api-key',
    DATALOGGER_TIMEOUT='0.123'
))
class TestScript(TestCase):
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_serial_port')
    def test_main_serial(self, read_serial_port_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Serial port input. """
        read_serial_port_mock.side_effect = [
            iter(['fake-serial-telegram']),
            StopIteration(),  # Stop loop after 1 round
        ]

        dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        # Check serial settings from file (defaults).
        self.assertTrue(read_serial_port_mock.called)
        self.assertEqual(read_serial_port_mock.call_args[1], dict(
            port='/dev/X',
            baudrate=12345,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=1,
            rtscts=0,
            timeout=0.123,
        ))

        # Check remote api call whether we have a telegram
        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)
        self.assertEqual(send_telegram_to_remote_dsmrreader_mock.call_args[1], dict(
            api_key='test-api-key',
            api_url='https://127.0.0.1:1234/api/v1/datalogger/dsmrreading',
            telegram='fake-serial-telegram',
            timeout=0.123
        ))

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_INPUT_METHOD='ipv4',
        DATALOGGER_NETWORK_HOST='127.1.1.0',
        DATALOGGER_NETWORK_PORT='23',
    ))
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_network_socket')
    def test_main_ipv4(self, read_network_socket_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Network socket input. """
        read_network_socket_mock.side_effect = [
            iter(['fake-network-telegram']),
            StopIteration(),  # Stop loop after 1 round
        ]

        dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        # Check serial settings from file (defaults).
        self.assertTrue(read_network_socket_mock.called)
        self.assertEqual(read_network_socket_mock.call_args[1], dict(
            host='127.1.1.0',
            port=23,
        ))

        # Check remote api call whether we have a telegram
        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)
        self.assertEqual(send_telegram_to_remote_dsmrreader_mock.call_args[1], dict(
            api_key='test-api-key',
            api_url='https://127.0.0.1:1234/api/v1/datalogger/dsmrreading',
            telegram='fake-network-telegram',
            timeout=0.123
        ))

    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_serial_port')
    def test_main_exception(self, read_serial_port_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Exception triggered by send_telegram_to_remote_dsmrreader(). """
        send_telegram_to_remote_dsmrreader_mock.side_effect = requests.exceptions.Timeout('Fake timeout')
        read_serial_port_mock.side_effect = [
            iter(['fake-telegram']),
            StopIteration(),
        ]

        dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_DEBUG_LOGGING='true',  # << Debugging enabled.
    ))
    @mock.patch('logging.Logger.setLevel')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_serial_port')
    def test_main_exception_with_debug_logging(
            self, read_serial_port_mock, send_telegram_to_remote_dsmrreader_mock, set_level_mock, *mocks
    ):
        """ Similar to test_main_exception(), but check DATALOGGER_DEBUG_LOGGING enabled. """
        send_telegram_to_remote_dsmrreader_mock.side_effect = requests.exceptions.Timeout('Fake timeout')
        read_serial_port_mock.side_effect = [
            iter(['fake-telegram']),
            StopIteration(),
        ]

        self.assertFalse(set_level_mock.called)

        dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertTrue(set_level_mock.called)
        self.assertEqual(set_level_mock.call_args[0][0], logging.DEBUG)
        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)

    @mock.patch('logging.error')
    @mock.patch('requests.post')
    def test_send_telegram_to_remote_dsmrreader(self, post_mock, error_logging_mock, *mocks):
        kwargs = dict(
            telegram='telegram-data',
            api_url='http://localhost/api',
            api_key='ABC',
            timeout=0.123
        )

        # Okay
        post_mock.return_value = mock.MagicMock(status_code=201)
        dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader(**kwargs)
        self.assertTrue(post_mock.called)
        self.assertEqual(post_mock.call_args[0][0], 'http://localhost/api')
        self.assertEqual(post_mock.call_args[1], dict(
            data=dict(telegram='telegram-data'),
            headers=dict(Authorization='Token ABC'),
            timeout=0.123,
        ))

        # Fail
        post_mock.reset_mock()
        post_mock.return_value = mock.MagicMock(status_code=400, text='Error message')
        dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader(**kwargs)
        self.assertTrue(post_mock.called)
        self.assertTrue(error_logging_mock.called)


@mock.patch.dict('os.environ', dict(
    DATALOGGER_API_HOSTS='http://127.0.0.1',
    DATALOGGER_API_KEYS='test',
    DATALOGGER_INPUT_METHOD='serial',
    DATALOGGER_SERIAL_PORT='/dev/X',
    DATALOGGER_SERIAL_BAUDRATE='12345',
))
class TestScriptErrors(TestCase):
    @mock.patch.dict('os.environ', dict(
        DATALOGGER_API_HOSTS='',
        DATALOGGER_API_KEYS='',
    ))
    def test_main_without_api_config(self):
        """ DATALOGGER_API_HOSTS / DATALOGGER_API_KEYS empty or omitted. """
        with self.assertRaises(RuntimeError) as e:
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertEqual(str(e.exception), 'API_HOSTS or API_KEYS not set')

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_API_HOSTS='http://127.0.0.1,https://localhost',
        DATALOGGER_API_KEYS='test',
    ))
    def test_main_with_inconsistent_api_config(self):
        """ DATALOGGER_API_HOSTS / DATALOGGER_API_KEYS count mismatch. """
        with self.assertRaises(RuntimeError) as e:
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertEqual(str(e.exception), 'The number of API_HOSTS and API_KEYS given do not match each other')

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_INPUT_METHOD='non-existing',
    ))
    def test_main_with_unsupported_input_method(self):
        """ Unsupported DATALOGGER_INPUT_METHOD. """
        with self.assertRaises(RuntimeError) as e:
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertEqual(str(e.exception), 'Unsupported DATALOGGER_INPUT_METHOD')
