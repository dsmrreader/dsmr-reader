import logging
import base64

from serial.serialutil import SerialException
from django.db.models.functions.datetime import TruncHour
from django.db.models.aggregates import Count
from django.db.models.expressions import F
from django.utils import timezone
from django.conf import settings
import serial
import pytz

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings, RetentionSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_datalogger.mapping import DSMR_MAPPING
from dsmr_parser import telegram_specifications
from dsmr_parser.exceptions import InvalidChecksumError, ParseError
from dsmr_parser.parsers import TelegramParser
import dsmr_datalogger.signals


dsmrreader_logger = logging.getLogger('dsmrreader')
django_logger = logging.getLogger('django')
commands_logger = logging.getLogger('commands')


def get_dsmr_connection_parameters():
    """ Returns the communication settings required for the DSMR version set. """
    DSMR_VERSION_MAPPING = {
        DataloggerSettings.DSMR_VERSION_2: {
            'baudrate': 9600,
            'bytesize': serial.SEVENBITS,
            'parity': serial.PARITY_EVEN,
            'specifications': telegram_specifications.V2_2,
        },
        DataloggerSettings.DSMR_VERSION_4_PLUS: {
            'baudrate': 115200,
            'bytesize': serial.EIGHTBITS,
            'parity': serial.PARITY_NONE,
            'specifications': telegram_specifications.V5,
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


def telegram_to_reading(data):
    """ Converts a P1 telegram to a DSMR reading, which will be stored in database. """
    params = get_dsmr_connection_parameters()
    parser = TelegramParser(params['specifications'])

    # We will log the telegrams in base64 for convenience and debugging.
    base64_data = base64.b64encode(data.encode())

    if settings.DSMRREADER_LOG_TELEGRAMS:
        dsmrreader_logger.info('Received telegram (base64 encoded): %s', base64_data)

    try:
        parsed_telegram = parser.parse(data)
    except (InvalidChecksumError, ParseError) as error:
        # Hook to keep track of failed readings count.
        MeterStatistics.objects.all().update(rejected_telegrams=F('rejected_telegrams') + 1)
        dsmrreader_logger.warning('Rejected telegram (%s) (base64 encoded): %s', error, base64_data)
        dsmrreader_logger.exception(error)
        raise InvalidTelegramError(error)

    return _map_telegram_to_model(parsed_telegram=parsed_telegram, data=data)


def _map_telegram_to_model(parsed_telegram, data):
    """ Maps parsed telegram to the fields. """
    READING_FIELDS = [x.name for x in DsmrReading._meta.get_fields() if x.name not in ('id', 'processed')]
    STATISTICS_FIELDS = [
        x.name for x in MeterStatistics._meta.get_fields() if x.name not in (
            'id', 'rejected_telegrams', 'latest_telegram'
        )
    ]

    model_fields = {k: None for k in READING_FIELDS + STATISTICS_FIELDS}

    for obis_ref, target_field in DSMR_MAPPING.items():
        try:
            parsed_ref = parsed_telegram[obis_ref]
        except KeyError:
            continue

        if isinstance(target_field, dict):
            model_fields[target_field['value']] = parsed_ref.value
            model_fields[target_field['datetime']] = parsed_ref.datetime
        else:
            model_fields[target_field] = parsed_ref.value

    # Hack for DSMR 2.x legacy, which lacks timestamp info.
    model_fields['timestamp'] = model_fields['timestamp'] or timezone.now()

    # For some reason, there are telegrams generated with a timestamp in the far future. We should disallow that.
    discard_timestamp = timezone.now() + timezone.timedelta(hours=24)

    if model_fields['timestamp'] > discard_timestamp or (
            model_fields['extra_device_timestamp'] is not None and
            model_fields['extra_device_timestamp'] > discard_timestamp):
        error_message = 'Discarded telegram with future timestamp(s): {} / {}'.format(
            model_fields['timestamp'], model_fields['extra_device_timestamp']
        )
        django_logger.error(error_message)
        raise InvalidTelegramError(error_message)

    # Now we need to split reading & statistics. So we split the dict here.
    reading_kwargs = {k: model_fields[k] for k in READING_FIELDS}
    statistics_kwargs = {k: model_fields[k] for k in STATISTICS_FIELDS}

    # Reading will be processed later.
    new_instance = DsmrReading.objects.create(**reading_kwargs)

    # There should already be one in database, created when migrating.
    statistics_kwargs['latest_telegram'] = data
    MeterStatistics.objects.all().update(**statistics_kwargs)

    # Broadcast this telegram as signal.
    dsmr_datalogger.signals.raw_telegram.send_robust(sender=None, data=data)

    return new_instance


def apply_data_retention():
    """
    When data retention is enabled, this discards all data applicable for retention. Keeps at least one data point per
    hour available.
    """
    retention_settings = RetentionSettings.get_solo()

    if retention_settings.data_retention_in_hours is None:
        # No retention enabled at all (default behaviour).
        return

    # These models should be rotated with retention. Dict value is the datetime field used.
    MODELS_TO_CLEANUP = {
        DsmrReading.objects.processed(): 'timestamp',
        ElectricityConsumption.objects.all(): 'read_at',
        GasConsumption.objects.all(): 'read_at',
    }

    retention_date = timezone.now() - timezone.timedelta(hours=retention_settings.data_retention_in_hours)

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
        )[:settings.DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN]

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
            commands_logger.debug('Retention | Cleaning up: %s (%s)', current_hour, data_set[0].__class__.__name__)
            data_set.exclude(pk__in=keeper_pks).delete()

    timezone.deactivate()
