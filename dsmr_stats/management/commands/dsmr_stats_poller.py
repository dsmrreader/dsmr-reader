import serial
from django.core.management.base import BaseCommand, CommandError

import dsmr_stats.services


class Command(BaseCommand):
    help = 'Polls the serial port for DSMR telegram and performs a reading.'

    def add_arguments(self, parser):
        parser.add_argument('--com_port', '-c', type=str, dest='com_port', default='/dev/ttyUSB0')

    def handle(self, **options):
        self._connect(options)

        try:
            self._read()
        except Exception as error:
            raise CommandError(error)

    def _connect(self, options):
        """ Initializes the serial port reader. Currently hardcoded for DSMR 4.0. """

        """
        Transfer speed and character formatting
        The interface will use a fixed transfer speed of 115200 baud. For character formatting a start
        bit, 8 data bits, no parity bit and a stop bit are used (8N1).Note this is not conforming to EN-
        IEC 62056-21 Mode D
        """
        self._serial = serial.Serial()
        self._serial.baudrate = 115200
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.parity = serial.PARITY_NONE
        self._serial.stopbits = serial.STOPBITS_ONE
        self._serial.xonxoff = 1
        self._serial.rtscts = 0
        self._serial.timeout = 20
        self._serial.port = options.get('com_port')

        try:
            self._serial.open()
        except serial.serialutil.SerialException as error:
            raise CommandError(error)

    def _read(self):
        """ Reads the serial port until we can create a reading point. """
        buffer = ''

        while True:
            data = self._serial.readline()

            try:
                # Make sure weird characters are converted properly.
                data = str(data, 'utf-8')
            except TypeError:
                pass

            # Reflect output to STDOUT for logging an convenience.
            print(data, end='')

            buffer += data

            # Telegrams start with '/' and ends with '!'. So we will use them as delimiters.
            if data.startswith('!'):
                # Create reading from buffer.
                return dsmr_stats.services.telegram_to_reading(data=buffer)
