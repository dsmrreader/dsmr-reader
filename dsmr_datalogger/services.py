import re

from django.utils import timezone
import serial

from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.dsmr import DSMR_MAPPING


def get_dsmr_connection_parameters():
    """ Returns the communication settings required for the DSMR version set. """
    DSMR_VERSION_MAPPING = {
        DataloggerSettings.DSMR_VERSION_3: {
            'baudrate': 9600,
            'bytesize': serial.SEVENBITS,
            'parity': serial.PARITY_EVEN,
        },
        DataloggerSettings.DSMR_VERSION_4: {
            'baudrate': 115200,
            'bytesize': serial.EIGHTBITS,
            'parity': serial.PARITY_NONE,
        },
    }

    datalogger_settings = DataloggerSettings.get_solo()
    connection_parameters = DSMR_VERSION_MAPPING[datalogger_settings.dsmr_version]
    connection_parameters['com_port'] = datalogger_settings.com_port
    return connection_parameters


def read_telegram():
    """ Reads the serial port until we can create a reading point. """
    connection_parameters = get_dsmr_connection_parameters()

    serial_handle = serial.Serial()
    serial_handle.port = connection_parameters['com_port']
    serial_handle.baudrate = connection_parameters['baudrate']
    serial_handle.bytesize = connection_parameters['bytesize']
    serial_handle.parity = connection_parameters['parity']
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
    Converts a P1 telegram to a DSMR reading, which will be stored in database.
    """

    def _get_reading_fields():
        reading_fields = DsmrReading._meta.get_all_field_names()
        reading_fields.remove('id')
        reading_fields.remove('processed')
        return reading_fields

    def _get_statistics_fields():
        reading_fields = MeterStatistics._meta.get_all_field_names()
        reading_fields.remove('id')
        return reading_fields

    parsed_reading = {}
    field_splitter = re.compile(r'([^(]+)\((.+)\)')

    for current_line in data.split("\n"):
        result = field_splitter.search(current_line)

        if not result:
            continue

        code = result.group(1)

        try:
            field = DSMR_MAPPING[code]
        except KeyError:
            continue

        value = result.group(2)

        # Drop units, as the database does not care for them.
        value = value.replace('*kWh', '').replace('*kW', '').replace('*m3', '')

        # Ugly workaround for combined values.
        if code == "0-1:24.2.1":
            timestamp_value, gas_usage = value.split(")(")
            parsed_reading[field[0]] = reading_timestamp_to_datetime(string=timestamp_value)
            parsed_reading[field[1]] = gas_usage
        else:
            if field == "timestamp":
                value = reading_timestamp_to_datetime(string=value)

            parsed_reading[field] = value

    # Now we need to split reading & statistics. So we split the dict here.
    reading_kwargs = {k: parsed_reading[k] for k in _get_reading_fields()}
    new_reading = DsmrReading.objects.create(**reading_kwargs)

    # Optional feature.
    if DataloggerSettings.get_solo().track_meter_statistics:
        statistics_kwargs = {k: parsed_reading[k] for k in _get_statistics_fields()}
        # There should already be one in database, created when migrating.
        MeterStatistics.objects.all().update(**statistics_kwargs)

    return new_reading


def reading_timestamp_to_datetime(string):
    """
    Converts a string containing a timestamp to a timezone aware datetime.
    """
    timestamp = re.search(r'(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})W', string)
    return timezone.make_aware(timezone.datetime(
        year=2000 + int(timestamp.group(1)),
        month=int(timestamp.group(2)),
        day=int(timestamp.group(3)),
        hour=int(timestamp.group(4)),
        minute=int(timestamp.group(5)),
        second=int(timestamp.group(6)),
    ))
