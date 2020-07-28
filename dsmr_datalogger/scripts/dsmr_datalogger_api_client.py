"""
    https://dsmr-reader.readthedocs.io/en/latest/installation/datalogger.html

    Installation:
        pip3 install pyserial==3.4 requests==2.24.0 python-decouple==3.3
"""
import datetime
import logging
import select
import socket
import time
import re

import serial
import requests
import decouple


def read_serial_port(port, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, timeout, **kwargs):  # noqa: C901
    """
    Opens the serial port, keeps reading until we have a full telegram and yields the result to preserve the connection.
    """
    logging.info('[%s] Opening serial port -> %s', datetime.datetime.now(), port)
    serial_handle = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        xonxoff=xonxoff,
        rtscts=rtscts,
        timeout=timeout,
    )

    telegram_start_seen = False
    buffer = ''

    while True:
        try:
            # We use an infinite datalogger loop and signals to break out of it. Serial
            # operations however do not work well with interrupts, so we'll have to check for E-INTR error.
            data = serial_handle.readline()
        except serial.SerialException as error:
            if str(error) == 'read failed: [Errno 4] Interrupted system call':
                # If we were signaled to stop, we still have to finish our loop.
                continue

            # Something else and unexpected failed.
            raise

        try:
            # Make sure weird characters are converted properly.
            data = str(data, 'utf-8')
        except TypeError:
            pass

        if data.startswith('/'):
            telegram_start_seen = True
            buffer = ''

        if telegram_start_seen:
            buffer += data

        if data.startswith('!') and telegram_start_seen:
            # Keep connection open.
            yield buffer


def read_network_socket(host, port):
    """ Opens a network socket and keeps reading until we have a full telegram. """
    MAX_SELECT_TIMEOUT = 0.5
    MAX_BYTES_RECV = 1024
    MAX_BUFFER = 10 * MAX_BYTES_RECV

    logging.info('[%s] Opening network socket -> %s:%d', datetime.datetime.now(), host, port)
    socket_handle = socket.socket(
        socket.AF_INET,  # Hardcoded ipv4, for now
        socket.SOCK_STREAM
    )

    try:
        socket_handle.connect((host, port))
    except Exception as error:
        raise RuntimeError('Failed to connect to network socket: {}', error)

    buffer = ''

    while True:
        rlist, _, _ = select.select([socket_handle], [], [], MAX_SELECT_TIMEOUT)

        if not rlist:
            continue

        # Usually a bad sign.
        if len(buffer) > MAX_BUFFER:
            logging.error(
                '[%s] Cleared buffer after reaching max size of %d Bytes!',
                datetime.datetime.now(),
                MAX_BUFFER
            )
            buffer = ''

        incoming_bytes = socket_handle.recv(MAX_BYTES_RECV)
        data = str(incoming_bytes, 'latin_1')
        buffer += data

        # Just add data to the buffer until we detect a telegram in it. Should work for 99% of the cases.
        match = re.search(r'(\/.+\![A-Z0-9]{4})', buffer, re.DOTALL)

        if not match:
            continue

        telegram = match.group(1)
        buffer = ''

        yield telegram


def _send_telegram_to_remote_dsmrreader(telegram, api_url, api_key, timeout):
    """ Registers a telegram by simply sending it to the application with a POST request. """
    logging.debug('[%s] Sending telegram to API: %s', datetime.datetime.now(), api_url)
    response = requests.post(
        api_url,
        headers={'Authorization': 'Token {}'.format(api_key)},
        data={'telegram': telegram},
        timeout=timeout,  # Prevents this script from hanging indefinitely when the server or network is unavailable.
    )

    if response.status_code != 201:
        logging.error('[%s] API error: HTTP %d - %s', datetime.datetime.now(), response.status_code, response.text)
        return

    logging.debug('[%s] API response OK: Telegram received successfully', datetime.datetime.now())


def _initialize_logging():
    logging_level = logging.INFO

    if decouple.config('DATALOGGER_DEBUG_LOGGING', default=False, cast=bool):
        logging_level = logging.DEBUG

    logging.getLogger().setLevel(logging_level)


def main():  # noqa: C901
    """ Entrypoint for command line execution only. """
    _initialize_logging()
    logging.info('[%s] Starting...', datetime.datetime.now())

    # Settings.
    DATALOGGER_SETTINGS = {}
    DATALOGGER_TIMEOUT = decouple.config('DATALOGGER_TIMEOUT', default=20, cast=float)
    DATALOGGER_SLEEP = decouple.config('DATALOGGER_SLEEP', default=0.5, cast=float)
    DATALOGGER_INPUT_METHOD = decouple.config('DATALOGGER_INPUT_METHOD')
    DATALOGGER_API_HOSTS = decouple.config('DATALOGGER_API_HOSTS', cast=decouple.Csv(post_process=tuple))
    DATALOGGER_API_KEYS = decouple.config('DATALOGGER_API_KEYS', cast=decouple.Csv(post_process=tuple))

    if not DATALOGGER_API_HOSTS or not DATALOGGER_API_KEYS:
        raise RuntimeError('API_HOSTS or API_KEYS not set')

    if len(DATALOGGER_API_HOSTS) != len(DATALOGGER_API_KEYS):
        raise RuntimeError('The number of API_HOSTS and API_KEYS given do not match each other')

    if DATALOGGER_INPUT_METHOD == 'serial':
        DATALOGGER_SETTINGS = dict(
            port=decouple.config('DATALOGGER_SERIAL_PORT'),
            baudrate=decouple.config('DATALOGGER_SERIAL_BAUDRATE', cast=int),
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=1,
            rtscts=0,
            timeout=DATALOGGER_TIMEOUT
        )
    elif DATALOGGER_INPUT_METHOD == 'ipv4':
        DATALOGGER_SETTINGS = dict(
            host=decouple.config('DATALOGGER_NETWORK_HOST'),
            port=decouple.config('DATALOGGER_NETWORK_PORT', cast=int),
        )

    try:
        input_function = {
            'serial': read_serial_port,
            'ipv4': read_network_socket,
        }[DATALOGGER_INPUT_METHOD]
    except KeyError:
        raise RuntimeError('Unsupported DATALOGGER_INPUT_METHOD')

    for telegram in input_function(**DATALOGGER_SETTINGS):
        logging.debug('[%s] Telegram read: %s', datetime.datetime.now(), telegram)

        for current_server_index in range(len(DATALOGGER_API_HOSTS)):
            current_api_host = DATALOGGER_API_HOSTS[current_server_index]
            current_api_url = '{}/api/v1/datalogger/dsmrreading'.format(current_api_host)
            current_api_key = DATALOGGER_API_KEYS[current_server_index]

            try:
                _send_telegram_to_remote_dsmrreader(
                    telegram=telegram,
                    api_url=current_api_url,
                    api_key=current_api_key,
                    timeout=DATALOGGER_TIMEOUT,
                )
            except Exception as error:
                logging.exception(error)

        time.sleep(DATALOGGER_SLEEP)


if __name__ == '__main__':  # pragma: no cover
    main()
