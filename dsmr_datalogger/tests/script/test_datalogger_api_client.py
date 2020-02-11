from unittest import mock

import requests
import serial
from django.test import TestCase

import dsmr_datalogger.scripts.dsmr_datalogger_api_client


@mock.patch('time.sleep')
class TestScript(TestCase):
    """
    This only tests the __main__ route and methods not covered by other tests.
    """
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.send_telegram_to_remote_dsmrreader')
    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.read_serial_port')
    def test_main(self, read_serial_port_mock, send_telegram_to_remote_dsmrreader_mock, *mocks):
        read_serial_port_mock.side_effect = [
            iter(['fake-telegram']),
            StopIteration(),  # Stop loop after 1 round
        ]

        dsmr_datalogger.scripts.dsmr_datalogger_api_client.main()

        # Check serial settings from file (defaults).
        self.assertTrue(read_serial_port_mock.called)
        self.assertEqual(read_serial_port_mock.call_args[1], dict(
            port='/dev/ttyUSB0',
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=1,
            rtscts=0,
            timeout=20,
        ))

        # Check remote api call when we have a telegram
        self.assertTrue(send_telegram_to_remote_dsmrreader_mock.called)
        self.assertEqual(send_telegram_to_remote_dsmrreader_mock.call_args[1], dict(
            api_key='APIKEY-1',
            api_url='http://HOST-OR-IP-1/api/v1/datalogger/dsmrreading',
            telegram='fake-telegram',
        ))

    @mock.patch('dsmr_datalogger.scripts.dsmr_datalogger_api_client.send_telegram_to_remote_dsmrreader')
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

    @mock.patch('logging.error')
    @mock.patch('requests.post')
    def test_send_telegram_to_remote_dsmrreader(self, post_mock, error_logging_mock, *mocks):
        kwargs = dict(
            telegram='telegram-data',
            api_url='http://localhost/api',
            api_key='ABC',
        )

        # Okay
        post_mock.return_value = mock.MagicMock(status_code=201)
        dsmr_datalogger.scripts.dsmr_datalogger_api_client.send_telegram_to_remote_dsmrreader(**kwargs)
        self.assertTrue(post_mock.called)
        self.assertEqual(post_mock.call_args[0][0], 'http://localhost/api')
        self.assertEqual(post_mock.call_args[1], dict(
            data=dict(telegram='telegram-data'),
            headers=dict(HTTP_AUTHORIZATION='Token ABC'),
            timeout=60,
        ))

        # Fail
        post_mock.reset_mock()
        post_mock.return_value = mock.MagicMock(status_code=400, text='Error message')
        dsmr_datalogger.scripts.dsmr_datalogger_api_client.send_telegram_to_remote_dsmrreader(**kwargs)
        self.assertTrue(post_mock.called)
        self.assertTrue(error_logging_mock.called)
