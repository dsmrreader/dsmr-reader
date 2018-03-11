"""
    NOTE: This script asumes:

    - Smart meter supporting DSMR v4+ (see settings around line 40).
    - The default serial port for the cable at ttyUSB0 (also see settings around line 40).

"""
from time import sleep

from serial.serialutil import SerialException
import requests
import serial


API_SERVERS = (
    # You can add multiple hosts here... just copy the line below and paste it directly under it.
    ('http://HOST-OR-IP/api/v1/datalogger/dsmrreading', 'APIKEY-BLABLABLA-ABCDEFGHI'),
)


def main():
    print('Starting...')

    for telegram in read_telegram():
        print('Telegram read')
        print(telegram)

        for current_server in API_SERVERS:
            api_url, api_key = current_server

            print('Sending telegram to:', api_url)

            try:
                send_telegram(telegram, api_url, api_key)
            except Exception as error:
                print('[!] {}'.format(error))

        sleep(1)


def read_telegram():
    """ Reads the serial port until we can create a reading point. """
    serial_handle = serial.Serial()
    serial_handle.port = '/dev/ttyUSB0'
    serial_handle.baudrate = 115200
    serial_handle.bytesize = serial.EIGHTBITS
    serial_handle.parity = serial.PARITY_NONE
    serial_handle.stopbits = serial.STOPBITS_ONE
    serial_handle.xonxoff = 1
    serial_handle.rtscts = 0
    serial_handle.timeout = 20

    # This might fail, but nothing we can do so just let it crash.
    serial_handle.open()

    telegram_start_seen = False
    buffer = ''

    # Just keep fetching data until we got what we were looking for.
    while True:
        try:
            data = serial_handle.readline()
        except SerialException as error:
            # Something else and unexpected failed.
            print('Serial connection failed:', error)
            raise StopIteration()  # Break out of yield.

        try:
            # Make sure weird characters are converted properly.
            data = str(data, 'utf-8')
        except TypeError:
            pass

        # This guarantees we will only parse complete telegrams. (issue #74)
        if data.startswith('/'):
            telegram_start_seen = True

            # But make sure to RESET any data collected as well! (issue #212)
            buffer = ''

        # Delay any logging until we've seen the start of a telegram.
        if telegram_start_seen:
            buffer += data

        # Telegrams ends with '!' AND we saw the start. We should have a complete telegram now.
        if data.startswith('!') and telegram_start_seen:
            yield buffer

            # Reset the flow again.
            telegram_start_seen = False
            buffer = ''


def send_telegram(telegram, api_url, api_key):
    # Register telegram by simply sending it to the application with a POST request.
    response = requests.post(
        api_url,
        headers={'X-AUTHKEY': api_key},
        data={'telegram': telegram},
    )

    # Old versions of DSMR-reader return 200, new ones 201.
    if response.status_code not in (200, 201):
        # Or you will find the error (hint) in the reponse body on failure.
        print('API error: {}'.format(response.text))


if __name__ == '__main__':
    main()
