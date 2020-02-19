import logging
import base64

from django.db.models.functions.datetime import TruncHour
from django.db.models.aggregates import Count
from django.db.models.expressions import F
from django.utils import timezone
from django.conf import settings
import serial
import pytz

from dsmr_backend.mixins import StopInfiniteRun
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings, RetentionSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_parser import telegram_specifications, obis_references
from dsmr_parser.exceptions import InvalidChecksumError, ParseError
from dsmr_parser.parsers import TelegramParser
from dsmr_datalogger.scripts.dsmr_datalogger_api_client import read_serial_port
import dsmr_datalogger.signals


dsmrreader_logger = logging.getLogger('dsmrreader')
django_logger = logging.getLogger('django')
commands_logger = logging.getLogger('commands')


def get_dsmr_connection_parameters():
    """ Returns the communication settings required for the DSMR version set. """
    DSMR_VERSION_MAPPING = {
        DataloggerSettings.DSMR_VERSION_2_3: telegram_specifications.V2_2,
        DataloggerSettings.DSMR_VERSION_4_PLUS: telegram_specifications.V5,
        DataloggerSettings.DSMR_BELGIUM_FLUVIUS: telegram_specifications.BELGIUM_FLUVIUS,
        DataloggerSettings.DSMR_LUXEMBOURG_SMARTY: telegram_specifications.LUXEMBOURG_SMARTY,
    }

    datalogger_settings = DataloggerSettings.get_solo()
    connection_parameters = dict(
        port=datalogger_settings.com_port,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        log_telegrams=datalogger_settings.log_telegrams,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=1,
        rtscts=0,
        timeout=20,
    )

    if datalogger_settings.dsmr_version == DataloggerSettings.DSMR_VERSION_2_3:
        connection_parameters.update({
            'baudrate': 9600,
            'bytesize': serial.SEVENBITS,
            'parity': serial.PARITY_EVEN,
        })

    connection_parameters.update(dict(
        specifications=DSMR_VERSION_MAPPING[datalogger_settings.dsmr_version]
    ))

    return connection_parameters


def read_and_process_telegram():
    """ Reads the serial port until we have a full telegram to parse and processes it. """

    # Partially reuse the remote datalogger.
    connection_parameters = get_dsmr_connection_parameters()
    del connection_parameters['log_telegrams']
    del connection_parameters['specifications']

    telegram_generator = read_serial_port(**connection_parameters)

    while True:
        try:
            telegram = next(telegram_generator)
        except Exception as error:
            commands_logger.exception(error)
            raise StopInfiniteRun()  # Do not ignore this situation, just tap out!

        try:
            dsmr_datalogger.services.telegram_to_reading(data=telegram)
        except InvalidTelegramError:
            pass

        yield  # Give back control to mixin, but preserve the connection.


def telegram_to_reading(data):
    """ Converts a P1 telegram to a DSMR reading, which will be stored in database. """
    params = get_dsmr_connection_parameters()
    parser = TelegramParser(params['specifications'])

    # We will log the telegrams in base64 for convenience and debugging.
    base64_data = base64.b64encode(data.encode())

    if params['log_telegrams']:
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
    mapping = _get_dsmrreader_mapping(DataloggerSettings.get_solo().dsmr_version)

    for obis_ref, obis_data in parsed_telegram.items():
        try:
            # Skip any fields we're not storing in our system.
            target_field = mapping[obis_ref]
        except KeyError:
            continue

        if isinstance(target_field, dict):
            model_fields[target_field['value']] = obis_data.value
            model_fields[target_field['datetime']] = obis_data.datetime
        else:
            model_fields[target_field] = obis_data.value

    # Defaults for telegrams with missing data.
    model_fields['timestamp'] = model_fields['timestamp'] or timezone.now()
    model_fields['electricity_delivered_2'] = model_fields['electricity_delivered_2'] or 0
    model_fields['electricity_returned_2'] = model_fields['electricity_returned_2'] or 0

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
            commands_logger.debug('Retention: Cleaning up: %s (%s)', current_hour, data_set[0].__class__.__name__)
            data_set.exclude(pk__in=keeper_pks).delete()

    timezone.deactivate()


def _get_dsmrreader_mapping(version):
    """ Returns the mapping for OBIS to DSMR-reader (model fields). """
    SPLIT_GAS_FIELD = {
        'value': 'extra_device_delivered',
        'datetime': 'extra_device_timestamp',
    }

    # Data stored in database for every reading.
    mapping = {
        obis_references.P1_MESSAGE_TIMESTAMP: 'timestamp',
        obis_references.ELECTRICITY_USED_TARIFF_1: 'electricity_delivered_1',
        obis_references.ELECTRICITY_DELIVERED_TARIFF_1: 'electricity_returned_1',
        obis_references.ELECTRICITY_USED_TARIFF_2: 'electricity_delivered_2',
        obis_references.ELECTRICITY_DELIVERED_TARIFF_2: 'electricity_returned_2',
        obis_references.CURRENT_ELECTRICITY_USAGE: 'electricity_currently_delivered',
        obis_references.CURRENT_ELECTRICITY_DELIVERY: 'electricity_currently_returned',

        obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_POSITIVE: 'phase_currently_delivered_l1',
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_POSITIVE: 'phase_currently_delivered_l2',
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_POSITIVE: 'phase_currently_delivered_l3',
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L1_NEGATIVE: 'phase_currently_returned_l1',
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L2_NEGATIVE: 'phase_currently_returned_l2',
        obis_references.INSTANTANEOUS_ACTIVE_POWER_L3_NEGATIVE: 'phase_currently_returned_l3',
        obis_references.INSTANTANEOUS_VOLTAGE_L1: 'phase_voltage_l1',
        obis_references.INSTANTANEOUS_VOLTAGE_L2: 'phase_voltage_l2',
        obis_references.INSTANTANEOUS_VOLTAGE_L3: 'phase_voltage_l3',

        # For some reason this identifier contains two fields, therefor we split them.
        obis_references.HOURLY_GAS_METER_READING: SPLIT_GAS_FIELD,
        obis_references.GAS_METER_READING: SPLIT_GAS_FIELD,  # Legacy

        # Static data, stored in database but only data of the last reading is preserved.
        obis_references.P1_MESSAGE_HEADER: 'dsmr_version',
        obis_references.ELECTRICITY_ACTIVE_TARIFF: 'electricity_tariff',
        obis_references.SHORT_POWER_FAILURE_COUNT: 'power_failure_count',
        obis_references.LONG_POWER_FAILURE_COUNT: 'long_power_failure_count',
        obis_references.VOLTAGE_SAG_L1_COUNT: 'voltage_sag_count_l1',
        obis_references.VOLTAGE_SAG_L2_COUNT: 'voltage_sag_count_l2',
        obis_references.VOLTAGE_SAG_L3_COUNT: 'voltage_sag_count_l3',
        obis_references.VOLTAGE_SWELL_L1_COUNT: 'voltage_swell_count_l1',
        obis_references.VOLTAGE_SWELL_L2_COUNT: 'voltage_swell_count_l2',
        obis_references.VOLTAGE_SWELL_L3_COUNT: 'voltage_swell_count_l3',
    }

    if version == DataloggerSettings.DSMR_BELGIUM_FLUVIUS:
        mapping.update({
            obis_references.BELGIUM_HOURLY_GAS_METER_READING: SPLIT_GAS_FIELD,
        })

    if version == DataloggerSettings.DSMR_LUXEMBOURG_SMARTY:
        mapping.update({
            obis_references.LUXEMBOURG_ELECTRICITY_USED_TARIFF_GLOBAL: 'electricity_delivered_1',
            obis_references.LUXEMBOURG_ELECTRICITY_DELIVERED_TARIFF_GLOBAL: 'electricity_returned_1',
        })

    return mapping
