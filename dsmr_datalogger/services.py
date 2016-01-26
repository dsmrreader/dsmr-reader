import re
import serial

from django.conf import settings
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import DataloggerSettings


def read_telegram():
    """ Reads the serial port until we can create a reading point. """
    """
    Transfer speed and character formatting
    ---------------------------------------
    The interface will use a fixed transfer speed of 115200 baud.
    For character formatting a start bit, 8 data bits, no parity bit and a
    stop bit are used (8N1).
    Note this is not conforming to EN-IEC 62056-21 Mode D
    """
    datalogger_settings = DataloggerSettings.get_solo()

    serial_handle = serial.Serial()
    serial_handle.baudrate = datalogger_settings.baud_rate
    serial_handle.port = datalogger_settings.com_port
    serial_handle.bytesize = serial.EIGHTBITS
    serial_handle.parity = serial.PARITY_NONE
    serial_handle.stopbits = serial.STOPBITS_ONE
    serial_handle.xonxoff = 1
    serial_handle.rtscts = 0
    serial_handle.timeout = 20

    # This might fail, but nothing we can do so just let it crash.
    serial_handle.open()

    buffer = ''

    while True:
        data = serial_handle.readline()

        try:
            # Make sure weird characters are converted properly.
            data = str(data, 'utf-8')
        except TypeError:
            pass

        buffer += data

        # Telegrams start with '/' and ends with '!'. So we will use them as delimiters.
        if data.startswith('!'):
            return buffer


def telegram_to_reading(data):
    """
    Converts a P1 telegram to a DSMR reading, stored in database.
    """
    reading_kwargs = {}
    field_splitter = re.compile(r'([^(]+)\((.+)\)')

    for current_line in data.split("\n"):
        result = field_splitter.search(current_line)

        if not result:
            continue

        code = result.group(1)

        try:
            field = DsmrReading.DSMR_MAPPING[code]
        except KeyError:
            continue

        value = result.group(2)

        # Drop units.
        value = value.replace('*kWh', '').replace('*kW', '').replace('*m3', '')

        # Ugly workaround for combined values.
        if code == "0-1:24.2.1":
            timestamp_value, gas_usage = value.split(")(")
            reading_kwargs[field[0]] = reading_timestamp_to_datetime(string=timestamp_value)
            reading_kwargs[field[1]] = gas_usage
        else:
            if field == "timestamp":
                value = reading_timestamp_to_datetime(string=value)

            reading_kwargs[field] = value

    return DsmrReading.objects.create(**reading_kwargs)


def reading_timestamp_to_datetime(string):
    """
    Converts a string containing a timestamp to a timezone aware datetime.
    """
    timestamp = re.search(r'(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})W', string)
    return timezone.datetime(
        year=2000 + int(timestamp.group(1)),
        month=int(timestamp.group(2)),
        day=int(timestamp.group(3)),
        hour=int(timestamp.group(4)),
        minute=int(timestamp.group(5)),
        second=int(timestamp.group(6)),
        tzinfo=settings.LOCAL_TIME_ZONE
    )
