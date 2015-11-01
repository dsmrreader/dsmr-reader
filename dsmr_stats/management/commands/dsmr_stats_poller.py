import serial
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Polls the serial port for DSMR readings'

    def add_arguments(self, parser):
        parser.add_argument('--com_port', '-c', nargs='+', type=str, dest='com_port', default='/dev/ttyUSB0')

    def handle(self, **options):
        self._connect(options)
        
        try:
            self._run()
        except Exception as error:
            raise CommandError(error)
        
    def _connect(self, options):
        """ Initializes the serial port reader. Currently hardcoded for DSMR 4.0. """
        self._serial = serial.Serial()
        self._serial.baudrate = 115200
        self._serial.bytesize=serial.EIGHTBITS
        self._serial.parity=serial.PARITY_NONE
        self._serial.stopbits=serial.STOPBITS_ONE
        self._serial.xonxoff=1
        self._serial.rtscts=0
        self._serial.timeout=20
        self._serial.port = options.get('com_port')
        
        try:
            self._serial.open()
        except serial.serialutil.SerialException as error:
            raise CommandError(error)

    def _run(self):
        """ Never ending loop, polling for data. """
        buffer = ""
        
        while True:
            data = self._serial.readline()
            print("data", data)
            buffer += data
