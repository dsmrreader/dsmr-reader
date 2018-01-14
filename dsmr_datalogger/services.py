import logging
import base64
import re

from serial.serialutil import SerialException
from django.db.models.functions.datetime import TruncHour
from django.db.models.aggregates import Count
from django.db.models.expressions import F
from django.utils import timezone
from django.conf import settings
import serial
import crcmod
import pytz

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings, RetentionSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_datalogger.dsmr import DSMR_MAPPING
import dsmr_datalogger.signals


dsmrreader_logger = logging.getLogger('dsmrreader')
django_logger = logging.getLogger('django')


def get_dsmr_connection_parameters():
    """ Returns the communication settings required for the DSMR version set. """
    DSMR_VERSION_MAPPING = {
        DataloggerSettings.DSMR_VERSION_2: {
            'baudrate': 9600,
            'bytesize': serial.SEVENBITS,
            'parity': serial.PARITY_EVEN,
            'crc': False,
        },
        DataloggerSettings.DSMR_VERSION_4_PLUS: {
            'baudrate': 115200,
            'bytesize': serial.EIGHTBITS,
            'parity': serial.PARITY_NONE,
            'crc': True,
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

    telegram_start_seen = False
    buffer = ''

    # Just keep fetching data until we got what we were looking for.
    while True:
        try:
            # Since #79 we use an infinite datalogger loop and signals to break out of it. Serial
            # operations however do not work well with interrupts, so we'll have to check for E-INTR.
            data = serial_handle.readline()
        except SerialException as error:
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
            serial_handle.close()
            return buffer


def verify_telegram_checksum(data):
    """
    Verifies telegram by checking it's CRC. Raises exception on failure. DSMR docs state:
    CRC is a CRC16 value calculated over the preceding characters in the data message (from / to ! using the polynomial)
    """
    matches = re.search(r'^(/[^!]+!)([A-Z0-9]{4})', data)

    try:
        content, crc = matches.groups()
    except AttributeError:
        # AttributeError: 'NoneType' object has no attribute 'groups'. This happens where there is not support for CRC.
        content = crc = None

    if not content or not crc:
        raise InvalidTelegramError('Content or CRC data not found')

    telegram = content.encode('ascii')  # TypeError: Unicode-objects must be encoded before calculating a CRC

    # DSMR docs: "The CRC value is represented as 4 hexadecimal characters (MSB first)". So just flip it back to int.
    telegram_checksum = int('0x{}'.format(crc), 0)  # For example: DD84 -> 0xDD84 -> 56708

    crc16_function = crcmod.predefined.mkPredefinedCrcFun('crc16')
    calculated_checksum = crc16_function(telegram)  # For example: 56708

    if telegram_checksum != calculated_checksum:
        raise InvalidTelegramError(
            'CRC mismatch: {} (telegram) != {} (calculated)'.format(telegram_checksum, calculated_checksum)
        )


def _convert_legacy_dsmr_gas_line(parsed_reading, current_line, next_line):
    """ Legacy support for DSMR 2.x gas. """
    legacy_gas_line = current_line

    if next_line.startswith('('):  # pragma: no cover
        legacy_gas_line = current_line + next_line

    legacy_gas_result = re.search(
        r'[^(]+\((\d+)\)\(\d+\)\(\d+\)\(\d+\)\([0-9-.:]+\)\(m3\)\(([0-9.]+)\)',
        legacy_gas_line
    )
    gas_timestamp = legacy_gas_result.group(1)

    if timezone.now().dst() != timezone.timedelta(0):
        gas_timestamp += 'S'
    else:
        gas_timestamp += 'W'

    parsed_reading['extra_device_timestamp'] = reading_timestamp_to_datetime(
        string=gas_timestamp
    )
    parsed_reading['extra_device_delivered'] = legacy_gas_result.group(2)
    return parsed_reading


def telegram_to_reading(data):  # noqa: C901
    """
    Converts a P1 telegram to a DSMR reading, which will be stored in database.
    """
    READING_FIELDS = [x.name for x in DsmrReading._meta.get_fields() if x.name not in ('id', 'processed')]
    STATISTICS_FIELDS = [
        x.name for x in MeterStatistics._meta.get_fields() if x.name not in ('id', 'rejected_telegrams')
    ]

    # We will log the telegrams in base64 for convenience and debugging 'n stuff.
    base64_data = base64.b64encode(data.encode())
    datalogger_settings = DataloggerSettings.get_solo()

    # Discard CRC check when any support is lacking anyway. Or when it's disabled.
    connection_parameters = get_dsmr_connection_parameters()

    if connection_parameters['crc'] and datalogger_settings.verify_telegram_crc:
        try:
            # Verify telegram by checking it's CRC.
            verify_telegram_checksum(data=data)
        except InvalidTelegramError as error:
            # Hook to keep track of failed readings count.
            MeterStatistics.objects.all().update(rejected_telegrams=F('rejected_telegrams') + 1)
            dsmrreader_logger.warning('Rejected telegram (base64 encoded): {}'.format(base64_data))
            dsmrreader_logger.exception(error)
            raise

    # Defaults all fields to NULL.
    parsed_reading = {k: None for k in READING_FIELDS + STATISTICS_FIELDS}
    field_splitter = re.compile(r'([^(]+)\((.+)\)')
    lines_read = data.split("\r\n")

    for index, current_line in enumerate(lines_read):
        result = field_splitter.search(current_line)

        if not result:
            continue

        code = result.group(1)

        # M-bus (0-n:24.1) cannot identify the type of device, see issue #92.
        if code in ('0-2:24.2.1', '0-3:24.2.1', '0-4:24.2.1'):
            code = '0-1:24.2.1'

        # DSMR 2.x emits gas readings in different format.
        if code == '0-1:24.3.0':
            parsed_reading = _convert_legacy_dsmr_gas_line(
                parsed_reading, current_line, lines_read[index + 1]
            )
            continue

        try:
            field = DSMR_MAPPING[code]
        except KeyError:
            continue

        value = result.group(2)

        # Drop units, as the database does not care for them.
        value = value.replace('*kWh', '').replace('*kW', '').replace('*m3', '')

        # Extra device parameters are placed on a single line, meh.
        if code == "0-1:24.2.1":
            timestamp_value, gas_usage = value.split(")(")
            parsed_reading[field[0]] = reading_timestamp_to_datetime(string=timestamp_value)
            parsed_reading[field[1]] = gas_usage
        else:
            if field == "timestamp":
                value = reading_timestamp_to_datetime(string=value)

            parsed_reading[field] = value

    # Hack for DSMR 2.x legacy, which lacks timestamp info..
    if parsed_reading['timestamp'] is None:
        parsed_reading['timestamp'] = timezone.now()

    # For some reason, there are telegrams generated with a timestamp in the far future. We should disallow that.
    discard_timestamp = timezone.now() + timezone.timedelta(hours=24)

    if parsed_reading['timestamp'] > discard_timestamp or (
            parsed_reading['extra_device_timestamp'] is not None and
            parsed_reading['extra_device_timestamp'] > discard_timestamp):
        error_message = 'Discarded telegram with future timestamp: {}'.format(data)
        django_logger.error(error_message)
        raise InvalidTelegramError(error_message)

    # Optional tracking of phases, but since we already mapped this above, just remove it again... :]
    if not datalogger_settings.track_phases:
        parsed_reading.update({
            'phase_currently_delivered_l1': None,
            'phase_currently_delivered_l2': None,
            'phase_currently_delivered_l3': None,
        })

    # Now we need to split reading & statistics. So we split the dict here.
    reading_kwargs = {k: parsed_reading[k] for k in READING_FIELDS}
    statistics_kwargs = {k: parsed_reading[k] for k in STATISTICS_FIELDS}

    # Reading will be processed later.
    new_reading = DsmrReading.objects.create(**reading_kwargs)

    # There should already be one in database, created when migrating.
    MeterStatistics.objects.all().update(**statistics_kwargs)

    # Broadcast this telegram as signal.
    dsmr_datalogger.signals.raw_telegram.send_robust(sender=None, data=data)

    if settings.DSMRREADER_LOG_TELEGRAMS:
        dsmrreader_logger.info('Received telegram (base64 encoded): {}'.format(base64_data))

    return new_reading


def reading_timestamp_to_datetime(string):
    """
    Converts a string containing a timestamp to a timezone aware datetime.
    """
    timestamp = re.search(r'(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})([WS])+', string)
    meter_timestamp = timezone.datetime(
        year=2000 + int(timestamp.group(1)),
        month=int(timestamp.group(2)),
        day=int(timestamp.group(3)),
        hour=int(timestamp.group(4)),
        minute=int(timestamp.group(5)),
        second=int(timestamp.group(6)),
    )
    is_dst = timestamp.group(7) == 'S'
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    return local_timezone.localize(meter_timestamp, is_dst=is_dst).astimezone(pytz.utc)


def apply_data_retention():
    """
    When data retention is enabled, this discards all data applicable for retention. Keeps at least one data point per
    hour available.
    """
    settings = RetentionSettings.get_solo()

    if settings.data_retention_in_hours is None:
        # No retention enabled at all (default behaviour).
        return

    current_hour = timezone.now().hour

    # Only cleanup during nights. Allow from midnight to six a.m.
    if current_hour > 6:
        return

    # Each run should be capped, for obvious performance reasons.
    MAX_HOURS_CLEANUP = 24

    # These models should be rotated with retention. Dict value is the datetime field used.
    MODELS_TO_CLEANUP = {
        DsmrReading.objects.processed(): 'timestamp',
        ElectricityConsumption.objects.all(): 'read_at',
        GasConsumption.objects.all(): 'read_at',
    }

    retention_date = timezone.now() - timezone.timedelta(hours=settings.data_retention_in_hours)

    # We need to force UTC here, to avoid AmbiguousTimeError's on DST changes.
    timezone.activate(pytz.UTC)

    for base_queryset, datetime_field in MODELS_TO_CLEANUP.items():
        hours_to_cleanup = base_queryset.filter(
            **{'{}__lt'.format(datetime_field): retention_date}
        ).annotate(
            item_hour=TruncHour(datetime_field)
        ).values('item_hour').annotate(
            item_count=Count('id')
        ).order_by().filter(
            item_count__gt=2
        ).order_by('item_hour').values_list(
            'item_hour', flat=True
        )[:MAX_HOURS_CLEANUP]

        hours_to_cleanup = list(hours_to_cleanup)  # Force evaluation.

        if not hours_to_cleanup:
            continue

        for current_hour in hours_to_cleanup:

            # Fetch all data per hour.
            data_set = base_queryset.filter(
                **{
                    '{}__gte'.format(datetime_field): current_hour,
                    '{}__lt'.format(datetime_field): current_hour + timezone.timedelta(hours=1),
                }
            )

            # Extract the first/last item, so we can exclude it.
            # NOTE: Want to alter this? Please update "item_count__gt=2" above as well!
            keeper_pks = [
                data_set.order_by(datetime_field)[0].pk,
                data_set.order_by('-{}'.format(datetime_field))[0].pk
            ]

            # Now drop all others.
            print('Retention | Cleaning up: {} ({})'.format(current_hour, data_set[0].__class__.__name__))
            data_set.exclude(pk__in=keeper_pks).delete()

    timezone.deactivate()
