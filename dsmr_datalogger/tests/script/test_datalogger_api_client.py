"""
This only tests the __main__ route and methods not covered by other tests.
"""
from unittest import mock
import logging

from django.test import TestCase
import requests
import serial
from serial import SerialException, Serial
from serial.urlhandler.protocol_socket import Serial as ProtocolSerial

import dsmr_datalogger.scripts.dsmr_datalogger_api_client


@mock.patch('time.sleep')
@mock.patch.dict('os.environ', dict(
    DATALOGGER_INPUT_METHOD='serial',
    DATALOGGER_SERIAL_PORT='/dev/X',
    DATALOGGER_SERIAL_BAUDRATE='12345',
    DATALOGGER_API_HOSTS='https://127.0.0.1:1234',
    DATALOGGER_API_KEYS='test-api-key',
    DATALOGGER_TIMEOUT='0.123',
    DATALOGGER_SLEEP='0.1',
    DATALOGGER_MIN_SLEEP_FOR_RECONNECT='999',

))
class TestScript(TestCase):
    @mock.patch.dict('os.environ', dict(
        DATALOGGER_SLEEP='0.1',
        DATALOGGER_MIN_SLEEP_FOR_RECONNECT='0',
    ))
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram')
    def test_main_no_reconnect(self, read_telegram_mock_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Persistent connection. """
        read_telegram_mock_mock.side_effect = [
            iter(['fake-serial-telegram']),
            StopIteration(),  # Stop loop after 1 round
        ]

        with self.assertRaises(StopIteration):
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram')
    def test_main_serial(self, read_telegram_mock_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Serial port input. """
        read_telegram_mock_mock.side_effect = [
            iter(['fake-serial-telegram']),
            StopIteration(),  # Stop loop after 1 round
        ]

        with self.assertRaises(StopIteration):
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        # Check serial settings from file (defaults).
        self.assertTrue(read_telegram_mock_mock.called)
        self.assertEqual(read_telegram_mock_mock.call_args[1], dict(
            url_or_port='/dev/X',
            telegram_timeout=0.123,
            baudrate=12345,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=1,
            rtscts=0,
        ))

        # Check remote api call whether we have a telegram
        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)
        self.assertEqual(send_telegram_to_remote_dsmrreader_mock.call_args[1], dict(
            api_key='test-api-key',
            api_url='https://127.0.0.1:1234/api/v1/datalogger/dsmrreading',
            telegram='fake-serial-telegram',
            timeout=0.123,
        ))

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_INPUT_METHOD='ipv4',
        DATALOGGER_NETWORK_HOST='127.1.1.0',
        DATALOGGER_NETWORK_PORT='23',
    ))
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram')
    def test_main_ipv4(self, read_telegram_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Network socket input. """
        read_telegram_mock.side_effect = [
            iter(['fake-network-telegram']),
            StopIteration(),  # Stop loop after 1 round
        ]

        with self.assertRaises(StopIteration):
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        # Check serial settings from file (defaults).
        self.assertTrue(read_telegram_mock.called)
        self.assertEqual(read_telegram_mock.call_args[1], dict(
            url_or_port='socket://127.1.1.0:23',
            telegram_timeout=0.123,
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
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram')
    def test_main_exception(self, read_telegram_mock_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        """ Exception triggered by send_telegram_to_remote_dsmrreader(). """
        send_telegram_to_remote_dsmrreader_mock.side_effect = requests.exceptions.Timeout('Fake timeout')
        read_telegram_mock_mock.side_effect = [
            iter(['fake-telegram']),
            StopIteration(),
        ]

        with self.assertRaises(StopIteration):
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_DEBUG_LOGGING='true',  # << Debugging enabled.
    ))
    @mock.patch('logging.Logger.setLevel')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client._send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram')
    def test_main_exception_with_debug_logging(
            self, read_telegram_mock_mock, send_telegram_to_remote_dsmrreader_mock, set_level_mock, *mocks
    ):
        """ Similar to test_main_exception(), but check DATALOGGER_DEBUG_LOGGING enabled. """
        send_telegram_to_remote_dsmrreader_mock.side_effect = requests.exceptions.Timeout('Fake timeout')
        read_telegram_mock_mock.side_effect = [
            iter(['fake-telegram']),
            StopIteration(),
        ]

        self.assertFalse(set_level_mock.called)

        with self.assertRaises(StopIteration):
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertTrue(set_level_mock.called)
        self.assertEqual(set_level_mock.call_args[0][0], logging.DEBUG)
        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)

    @mock.patch.dict('os.environ', dict(
        DATALOGGER_DEBUG_LOGGING='false',  # << Debugging disabled.
    ))
    @mock.patch('logging.Logger.setLevel')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram')
    def test_main_without_debug_logging(self, read_telegram_mock_mock, set_level_mock, *mocks):
        """ Similar to test_main_exception_with_debug_logging(), but check DATALOGGER_DEBUG_LOGGING disabled. """
        read_telegram_mock_mock.return_value = iter([])

        with self.assertRaises(StopIteration):
            dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        self.assertTrue(set_level_mock.called)
        self.assertEqual(set_level_mock.call_args[0][0], logging.INFO)

    @mock.patch('logging.Logger.error')
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
    DATALOGGER_DSMR_VERSION='4',
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


@mock.patch('serial.serial_for_url')
class TestScriptSerialSocket(TestCase):
    """ Serial port test. """

    def test_connection_error(self, serial_for_url_mock):
        """ Connection error. """
        serial_for_url_mock.side_effect = SerialException('Something happened')

        generator = dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram(
            url_or_port='/dev/X',
            telegram_timeout=999
        )
        with self.assertRaises(RuntimeError):
            next(generator)

    def test_telegram_timeout(self, serial_for_url_mock):
        """ It took too long to detect a telegram. """
        cli_serial = Serial()
        cli_serial.read = mock.MagicMock(return_value=bytes('!@#$%', 'utf8'))  # Garbage data will never match telegram
        serial_for_url_mock.return_value = cli_serial

        generator = dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram(
            url_or_port='/dev/X',
            telegram_timeout=0.001  # This should simulate it for real.
        )
        with self.assertRaises(RuntimeError):
            next(generator)

    def test_read(self, serial_for_url_mock):
        cli_serial = Serial()
        cli_serial.read = mock.MagicMock(side_effect=[
            # Splitted over multiple reads.
            bytes('', 'utf8'),
            bytes("garbage!@*!/fake-", 'utf8'),
            bytes('telegram!1234', 'utf8'),
        ])
        serial_for_url_mock.return_value = cli_serial

        generator = dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram(
            url_or_port='/dev/X',
            telegram_timeout=5
        )
        telegram = next(generator)
        self.assertEqual(telegram, "/fake-telegram!1234")


@mock.patch('serial.serial_for_url')
class TestScriptNetworkSocket(TestCase):
    """ Network socket test. """

    def _call_datalogger(self):
        return

    def test_read(self, serial_for_url_mock):
        protocol_serial = ProtocolSerial()
        protocol_serial.read = mock.MagicMock(side_effect=[
            bytes('', 'utf8'),
            bytes("garbage!@*!/fake-", 'utf8'),
            bytes('telegram!1234', 'utf8'),
            bytes("/other-telegram!5678", 'utf8')
        ])
        protocol_serial.reset_input_buffer = mock.MagicMock()
        serial_for_url_mock.return_value = protocol_serial

        generator = dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_telegram(
            url_or_port='socket://localhost:23',
            telegram_timeout=5
        )
        telegram = next(generator)
        self.assertEqual(telegram, "/fake-telegram!1234")

        # Read again for second telegram.
        telegram = next(generator)
        self.assertEqual(telegram, "/other-telegram!5678")
