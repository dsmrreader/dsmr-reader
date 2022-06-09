import datetime
from datetime import time
from decimal import Decimal, ROUND_HALF_UP
import logging
from typing import Dict, Optional, List, Tuple

import pytz
from django.conf import settings
from django.db.models import Avg, Min, Max, Count, Manager
from django.db.utils import IntegrityError
from django.utils import timezone, formats

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_consumption.exceptions import CompactorNotReadyError
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption, \
    QuarterHourPeakElectricityConsumption
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.statistics import DayStatistics
from dsmr_weather.models.reading import TemperatureReading
from dsmr_stats.models.note import Note
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_backend.services.backend


logger = logging.getLogger('dsmrreader')


def run(scheduled_process: ScheduledProcess) -> None:
    """ Compacts all unprocessed readings, capped by a max to prevent hanging backend. """
    for current_reading in DsmrReading.objects.unprocessed()[0:settings.DSMRREADER_COMPACT_MAX]:
        try:
            compact(dsmr_reading=current_reading)
        except CompactorNotReadyError:
            # Try again in a while, since we can't do anything now anyway.
            scheduled_process.delay(seconds=15)
            return

    scheduled_process.delay(seconds=1)


def run_quarter_hour_peaks(scheduled_process: ScheduledProcess) -> None:
    """ Calculates the quarter-hour peak consumption. For background info see issue #1084 ."""
    MINUTE_INTERVAL = 15

    # Just start with whatever time this process was scheduled.
    # As it's incremental and will fix data gaps (see further below).
    fuzzy_start = scheduled_process.planned.replace(second=0, microsecond=0)

    # The fuzzy start should be just beyond whatever we target. E.g. fuzzy start = currently 14:34
    logger.debug('Quarter hour peaks: Using %s as fuzzy start', timezone.localtime(fuzzy_start))

    # Rewind at least 15 minutes. E.g. currently 14:34 -> 14:19 (rewind_minutes = 15)
    rewind_minutes = MINUTE_INTERVAL

    # Map to xx:00, xx:15, xx:30 or xx:45. E.g. 14:19 -> 14:15. Makes 19 % 15 = 4 (rewind_minutes = 15 + 4)
    rewind_minutes += (
        fuzzy_start - timezone.timedelta(minutes=rewind_minutes)
    ).minute % MINUTE_INTERVAL

    # E.g. Fuzzy start was 14:34. Now we start/end at 14:15/14:30.
    start = fuzzy_start - timezone.timedelta(minutes=rewind_minutes)
    end = start + timezone.timedelta(minutes=MINUTE_INTERVAL)

    # Do NOT continue until we've received new readings AFTER the targeted end. Ensuring we do not miss any and it also
    # blocks the "self-healing" implementation when having data gaps.
    # Only happens for data gaps or directly after new installations (edge cases). This will keep pushing forward.
    if not DsmrReading.objects.filter(timestamp__gte=end).exists():
        logger.debug(
            'Quarter hour peaks: Ready but awaiting any new readings after %s, postponing for a bit...',
            timezone.localtime(end),
        )

        # Assumes new readings will arrive shortly (for most users/setups)
        scheduled_process.postpone(seconds=5)
        return

    quarter_hour_readings = DsmrReading.objects.filter(timestamp__gte=start, timestamp__lte=end)

    # Only happens for data gaps or directly after new installations (edge cases). This will keep pushing forward.
    if len(quarter_hour_readings) < 2:
        logger.warning(
            'Quarter hour peaks: Ready but not enough readings found between %s - %s, skipping quarter...',
            timezone.localtime(start),
            timezone.localtime(end),
        )
        scheduled_process.postpone(minutes=MINUTE_INTERVAL)
        return

    first_reading = quarter_hour_readings.first()
    last_reading = quarter_hour_readings.last()
    logger.debug(
        'Quarter hour peaks: Quarter %s - %s resulted in readings %s - %s',
        timezone.localtime(start),
        timezone.localtime(end),
        timezone.localtime(first_reading.timestamp),
        timezone.localtime(last_reading.timestamp),
    )

    # Do not create duplicate data.
    existing_data = QuarterHourPeakElectricityConsumption.objects.filter(
        read_at_start__gte=start,
        read_at_start__lte=end,
    ).exists()

    if existing_data:
        logger.debug('Quarter hour peaks: Ready but quarter already processed, rescheduling for next quarter...')
        scheduled_process.reschedule(planned_at=end + timezone.timedelta(minutes=MINUTE_INTERVAL))
        return

    # Calculate quarter data.
    total_delivered_start = first_reading.electricity_delivered_1 + first_reading.electricity_delivered_2
    total_delivered_end = last_reading.electricity_delivered_1 + last_reading.electricity_delivered_2
    avg_delivered_in_quarter = total_delivered_end - total_delivered_start
    logger.debug(
        'Quarter hour peaks: Calculating for %s - %s',
        timezone.localtime(first_reading.timestamp),
        timezone.localtime(last_reading.timestamp),
    )

    new_instance = QuarterHourPeakElectricityConsumption.objects.create(
        # Using the reading timestamps used to ensure we can indicate gaps or lag in reading input.
        # E.g. due backend/datalogger process sleep or simply v4 meters emitting a reading only once per 10 seconds.
        read_at_start=first_reading.timestamp,
        read_at_end=last_reading.timestamp,
        # avg_delivered_in_quarter = kW QUARTER peak during 15 minutes... x 4 maps it to avg per hour for kW HOUR peak
        average_delivered=avg_delivered_in_quarter * 4
    )
    logger.debug('Quarter hour peaks: Created %s', new_instance)

    # Reschedule around the next moment we can expect to process the next quarter. Also works retroactively/with gaps.
    scheduled_process.reschedule(
        planned_at=new_instance.read_at_end + timezone.timedelta(minutes=MINUTE_INTERVAL)
    )


def compact(dsmr_reading: DsmrReading) -> None:
    """ Compacts/converts DSMR readings to consumption data. Optionally groups electricity by minute. """
    consumption_settings = ConsumptionSettings.get_solo()

    # Grouping by minute requires some distinction and history checking.
    reading_start = timezone.datetime.combine(
        dsmr_reading.timestamp.date(),
        time(hour=dsmr_reading.timestamp.hour, minute=dsmr_reading.timestamp.minute),
    ).replace(tzinfo=pytz.UTC)

    if consumption_settings.electricity_grouping_type == ConsumptionSettings.ELECTRICITY_GROUPING_BY_MINUTE:
        system_time_past_minute = timezone.now() >= reading_start + timezone.timedelta(minutes=1)
        reading_past_minute_exists = DsmrReading.objects.filter(
            timestamp__gte=reading_start + timezone.timedelta(minutes=1)
        ).exists()

        # Postpone until the minute has passed on the system time. And when there are (new) readings beyond this minute.
        if not system_time_past_minute or not reading_past_minute_exists:
            logger.debug('Compact: Waiting for newer readings before grouping data...')
            raise CompactorNotReadyError()

    # Create consumption records.
    _compact_electricity(
        dsmr_reading=dsmr_reading,
        electricity_grouping_type=consumption_settings.electricity_grouping_type,
        reading_start=reading_start
    )
    _compact_gas(
        dsmr_reading=dsmr_reading,
        gas_grouping_type=consumption_settings.gas_grouping_type
    )

    dsmr_reading.processed = True
    dsmr_reading.save(update_fields=['processed'])

    logger.debug('Compact: Processed reading: %s', dsmr_reading)


def _compact_electricity(
    dsmr_reading: DsmrReading, electricity_grouping_type: int, reading_start: timezone.datetime
) -> None:
    """
    Compacts any DSMR readings to electricity consumption records, optionally grouped.
    """

    if electricity_grouping_type == ConsumptionSettings.ELECTRICITY_GROUPING_BY_READING:
        try:
            # NO grouping, so the data will be stored as is.
            ElectricityConsumption.objects.get_or_create(
                read_at=dsmr_reading.timestamp,
                delivered_1=dsmr_reading.electricity_delivered_1,
                returned_1=dsmr_reading.electricity_returned_1,
                delivered_2=dsmr_reading.electricity_delivered_2,
                returned_2=dsmr_reading.electricity_returned_2,
                currently_delivered=dsmr_reading.electricity_currently_delivered,
                currently_returned=dsmr_reading.electricity_currently_returned,
                phase_currently_delivered_l1=dsmr_reading.phase_currently_delivered_l1,
                phase_currently_delivered_l2=dsmr_reading.phase_currently_delivered_l2,
                phase_currently_delivered_l3=dsmr_reading.phase_currently_delivered_l3,
                phase_currently_returned_l1=dsmr_reading.phase_currently_returned_l1,
                phase_currently_returned_l2=dsmr_reading.phase_currently_returned_l2,
                phase_currently_returned_l3=dsmr_reading.phase_currently_returned_l3,
                phase_voltage_l1=dsmr_reading.phase_voltage_l1,
                phase_voltage_l2=dsmr_reading.phase_voltage_l2,
                phase_voltage_l3=dsmr_reading.phase_voltage_l3,
                phase_power_current_l1=dsmr_reading.phase_power_current_l1,
                phase_power_current_l2=dsmr_reading.phase_power_current_l2,
                phase_power_current_l3=dsmr_reading.phase_power_current_l3,
            )
        except IntegrityError:
            # This might happen, even though rarely, when the same timestamp with different values comes by.
            pass

        return

    minute_end = reading_start + timezone.timedelta(minutes=1)

    # We might have multiple readings per minute, so there is a chance we already parsed it a moment ago.
    if ElectricityConsumption.objects.filter(read_at=minute_end).exists():
        return

    grouped_reading = DsmrReading.objects.filter(
        timestamp__gte=reading_start, timestamp__lt=minute_end
    ).aggregate(
        # Average Watt
        avg_delivered=Avg('electricity_currently_delivered'),
        avg_returned=Avg('electricity_currently_returned'),
        # Take the most recent (highest) meter positions
        max_delivered_1=Max('electricity_delivered_1'),
        max_delivered_2=Max('electricity_delivered_2'),
        max_returned_1=Max('electricity_returned_1'),
        max_returned_2=Max('electricity_returned_2'),
        # Average all other data.
        avg_phase_delivered_l1=Avg('phase_currently_delivered_l1'),
        avg_phase_delivered_l2=Avg('phase_currently_delivered_l2'),
        avg_phase_delivered_l3=Avg('phase_currently_delivered_l3'),
        avg_phase_return_l1=Avg('phase_currently_returned_l1'),
        avg_phase_return_l2=Avg('phase_currently_returned_l2'),
        avg_phase_return_l3=Avg('phase_currently_returned_l3'),
        avg_phase_voltage_l1=Avg('phase_voltage_l1'),
        avg_phase_voltage_l2=Avg('phase_voltage_l2'),
        avg_phase_voltage_l3=Avg('phase_voltage_l3'),
        avg_phase_power_current_l1=Avg('phase_power_current_l1'),
        avg_phase_power_current_l2=Avg('phase_power_current_l2'),
        avg_phase_power_current_l3=Avg('phase_power_current_l3'),
    )

    ElectricityConsumption.objects.create(
        read_at=minute_end,
        delivered_1=grouped_reading['max_delivered_1'],
        returned_1=grouped_reading['max_returned_1'],
        delivered_2=grouped_reading['max_delivered_2'],
        returned_2=grouped_reading['max_returned_2'],
        currently_delivered=grouped_reading['avg_delivered'],
        currently_returned=grouped_reading['avg_returned'],
        phase_currently_delivered_l1=grouped_reading['avg_phase_delivered_l1'],
        phase_currently_delivered_l2=grouped_reading['avg_phase_delivered_l2'],
        phase_currently_delivered_l3=grouped_reading['avg_phase_delivered_l3'],
        phase_currently_returned_l1=grouped_reading['avg_phase_return_l1'],
        phase_currently_returned_l2=grouped_reading['avg_phase_return_l2'],
        phase_currently_returned_l3=grouped_reading['avg_phase_return_l3'],
        phase_voltage_l1=grouped_reading['avg_phase_voltage_l1'],
        phase_voltage_l2=grouped_reading['avg_phase_voltage_l2'],
        phase_voltage_l3=grouped_reading['avg_phase_voltage_l3'],
        phase_power_current_l1=grouped_reading['avg_phase_power_current_l1'],
        phase_power_current_l2=grouped_reading['avg_phase_power_current_l2'],
        phase_power_current_l3=grouped_reading['avg_phase_power_current_l3'],
    )


def _compact_gas(dsmr_reading: DsmrReading, gas_grouping_type: int) -> None:
    """
    Compacts any DSMR readings to gas consumption records, optionally grouped. Only when there is support for gas.

    There is quite some distinction between DSMR v4 and v5. DSMR v4 will update only once per hour and backtracks the
    time by reporting it over the previous hour.
    DSMR v5 will just allow small intervals, depending on whether the readings are grouped per minute or not.
    """
    if not dsmr_reading.extra_device_timestamp or not dsmr_reading.extra_device_delivered:
        # Some households aren't connected to a gas meter at all.
        return

    gas_read_at = dsmr_reading.extra_device_timestamp
    dsmr_version = MeterStatistics.get_solo().dsmr_version

    # User requests grouping? Truncate any precision, making the gas reading's timestamp collide with the previous one,
    # until at least an hour passed by.
    if gas_grouping_type == ConsumptionSettings.GAS_GROUPING_BY_HOUR:
        gas_read_at = gas_read_at.replace(minute=0, second=0, microsecond=0)

    # DSMR v4 readings should reflect to the previous hour, to keep it compatible with the existing implementation.
    if dsmr_version is not None and dsmr_version.startswith('4'):
        gas_read_at = gas_read_at - timezone.timedelta(hours=1)

    # We will not override data, just ignore it. Also subject to DSMR v4 and grouped gas readings.
    if GasConsumption.objects.filter(read_at=gas_read_at).exists():
        return

    # DSMR protocol does not expose current gas rate, so we have to calculate it ourselves.
    # Relative to the previous gas consumption, if any.
    try:
        previous = GasConsumption.objects.filter(
            # LT filter prevents negative values when importing historic data.
            read_at__lt=gas_read_at
        ).order_by('-read_at')[0]
    except IndexError:
        gas_diff = 0
    else:
        gas_diff = dsmr_reading.extra_device_delivered - previous.delivered

    GasConsumption.objects.create(
        read_at=gas_read_at,
        delivered=dsmr_reading.extra_device_delivered,
        currently_delivered=gas_diff
    )


def consumption_by_range(start, end) -> Tuple[Manager, Manager]:
    """ Calculates the consumption of a range specified. """
    electricity_readings = ElectricityConsumption.objects.filter(
        read_at__gte=start, read_at__lt=end,
    ).order_by('read_at')

    gas_readings = GasConsumption.objects.filter(
        read_at__gte=start, read_at__lt=end,
    ).order_by('read_at')

    return electricity_readings, gas_readings


def day_consumption(day: datetime.date) -> Dict:
    """ Calculates the consumption of an entire day. """
    consumption = {
        'day': day
    }
    hours_in_day = dsmr_backend.services.backend.hours_in_day(day=day)
    day_start = timezone.make_aware(timezone.datetime(year=day.year, month=day.month, day=day.day))
    day_end = day_start + timezone.timedelta(hours=hours_in_day)

    try:
        daily_energy_price = get_day_prices(day=day)
    except EnergySupplierPrice.DoesNotExist:
        daily_energy_price = get_fallback_prices()

    electricity_readings, gas_readings = consumption_by_range(start=day_start, end=day_end)

    if not electricity_readings.exists():
        raise LookupError("No electricity readings found for: {}".format(day))

    electricity_reading_count = electricity_readings.count()

    first_reading = electricity_readings[0]
    last_reading = electricity_readings[electricity_reading_count - 1]

    consumption['latest_consumption'] = last_reading
    consumption['electricity1'] = last_reading.delivered_1 - first_reading.delivered_1
    consumption['electricity2'] = last_reading.delivered_2 - first_reading.delivered_2
    consumption['electricity1_start'] = first_reading.delivered_1
    consumption['electricity1_end'] = last_reading.delivered_1
    consumption['electricity2_start'] = first_reading.delivered_2
    consumption['electricity2_end'] = last_reading.delivered_2
    consumption['electricity1_returned'] = last_reading.returned_1 - first_reading.returned_1
    consumption['electricity2_returned'] = last_reading.returned_2 - first_reading.returned_2
    consumption['electricity1_returned_start'] = first_reading.returned_1
    consumption['electricity1_returned_end'] = last_reading.returned_1
    consumption['electricity2_returned_start'] = first_reading.returned_2
    consumption['electricity2_returned_end'] = last_reading.returned_2
    consumption['electricity_merged'] = consumption['electricity1'] + consumption['electricity2']
    consumption['electricity_returned_merged'] = \
        consumption['electricity1_returned'] + consumption['electricity2_returned']

    # Cost per tariff. Taking electricity return into account.
    consumption['electricity1_cost'] = round_decimal(
        (
            consumption['electricity1'] * daily_energy_price.electricity_delivered_1_price
        ) - (
            consumption['electricity1_returned'] * daily_energy_price.electricity_returned_1_price
        )
    )
    consumption['electricity2_cost'] = round_decimal(
        (
            consumption['electricity2'] * daily_energy_price.electricity_delivered_2_price
        ) - (
            consumption['electricity2_returned'] * daily_energy_price.electricity_returned_2_price
        )
    )

    # Totals.
    consumption['electricity_cost_merged'] = consumption['electricity1_cost'] + consumption['electricity2_cost']
    consumption['total_cost'] = consumption['electricity_cost_merged']

    # Gas readings are optional, as not all meters support this.
    if gas_readings.exists():
        gas_reading_count = gas_readings.count()
        first_reading = gas_readings[0]
        last_reading = gas_readings[gas_reading_count - 1]
        consumption['gas'] = last_reading.delivered - first_reading.delivered
        consumption['gas_start'] = first_reading.delivered
        consumption['gas_end'] = last_reading.delivered
        consumption['gas_cost'] = round_decimal(
            consumption['gas'] * daily_energy_price.gas_price
        )
        consumption['total_cost'] += consumption['gas_cost']

    # Fixed costs.
    consumption['fixed_cost'] = round_decimal(daily_energy_price.fixed_daily_cost)
    consumption['total_cost'] += daily_energy_price.fixed_daily_cost  # Raw, not rounded
    consumption['total_cost'] = round_decimal(consumption['total_cost'])

    # Current prices as well.
    consumption['energy_supplier_price_electricity_delivered_1'] = daily_energy_price.electricity_delivered_1_price
    consumption['energy_supplier_price_electricity_delivered_2'] = daily_energy_price.electricity_delivered_2_price
    consumption['energy_supplier_price_electricity_returned_1'] = daily_energy_price.electricity_returned_1_price
    consumption['energy_supplier_price_electricity_returned_2'] = daily_energy_price.electricity_returned_2_price
    consumption['energy_supplier_price_gas'] = daily_energy_price.gas_price
    consumption['energy_supplier_price_fixed_daily_cost'] = daily_energy_price.fixed_daily_cost

    # Any notes of that day.
    consumption['notes'] = Note.objects.filter(day=day).values_list('description', flat=True)

    # Temperature readings are not mandatory as well.
    temperature_readings = TemperatureReading.objects.filter(
        read_at__gte=day_start, read_at__lt=day_end,
    ).order_by('read_at')
    consumption['lowest_temperature'] = temperature_readings.aggregate(
        avg_temperature=Min('degrees_celcius'),
    )['avg_temperature'] or 0
    consumption['highest_temperature'] = temperature_readings.aggregate(
        avg_temperature=Max('degrees_celcius'),
    )['avg_temperature'] or 0
    consumption['average_temperature'] = temperature_readings.aggregate(
        avg_temperature=Avg('degrees_celcius'),
    )['avg_temperature'] or 0
    consumption['average_temperature'] = round_decimal(consumption['average_temperature'])

    return consumption


def live_electricity_consumption() -> Dict:
    """ Returns the current latest/live electricity consumption. """
    data = {}

    try:
        latest_reading = DsmrReading.objects.all().order_by('-timestamp')[0]
    except IndexError:
        return data

    latest_timestamp = timezone.localtime(latest_reading.timestamp)

    # In case the smart meter's clock is running in the future.
    latest_timestamp = min(timezone.now(), latest_timestamp)

    data['timestamp'] = latest_timestamp
    data['currently_delivered'] = int(latest_reading.electricity_currently_delivered * 1000)
    data['currently_returned'] = int(latest_reading.electricity_currently_returned * 1000)
    data['cost_per_hour'] = None
    data['tariff_name'] = None

    tariff = MeterStatistics.get_solo().electricity_tariff
    frontend_settings = FrontendSettings.get_solo()
    tariff_names = {
        1: frontend_settings.tariff_1_delivered_name.capitalize(),
        2: frontend_settings.tariff_2_delivered_name.capitalize(),
    }

    try:
        data['tariff_name'] = tariff_names[tariff]
    except KeyError:
        pass

    try:
        prices = get_day_prices(day=timezone.now().date())
    except EnergySupplierPrice.DoesNotExist:
        return data

    delivered_prices_per_tariff = {
        1: prices.electricity_delivered_1_price,
        2: prices.electricity_delivered_2_price,
    }
    returned_prices_per_tariff = {
        1: prices.electricity_returned_1_price,
        2: prices.electricity_returned_2_price,
    }

    try:
        delivered_cost_per_hour = latest_reading.electricity_currently_delivered * delivered_prices_per_tariff[tariff]
        returned_cost_per_hour = latest_reading.electricity_currently_returned * returned_prices_per_tariff[tariff]
    except KeyError:
        return data

    # Some users have a setup that delivers and returns simultaneously. So we need to take both into account.
    data['cost_per_hour'] = formats.number_format(round_decimal(
        delivered_cost_per_hour - returned_cost_per_hour
    ))

    return data


def live_gas_consumption() -> Dict:
    """ Returns the current latest/live gas consumption. """
    data = {}

    try:
        latest_data = GasConsumption.objects.all().order_by('-read_at')[0]
    except IndexError:
        # Don't even bother when no data available.
        return data

    data['timestamp'] = timezone.localtime(latest_data.read_at)
    data['currently_delivered'] = latest_data.currently_delivered

    try:
        prices = get_day_prices(day=timezone.now().date())
    except EnergySupplierPrice.DoesNotExist:
        return data

    # Note that we use generic 'interval' here, as it may differ, depending on the smart meter's protocol version.
    data['cost_per_interval'] = formats.number_format(
        round_decimal(latest_data.currently_delivered * prices.gas_price)
    )

    return data


def round_decimal(value, decimal_count: int = 2) -> Decimal:
    """ Rounds a value to X decimals. """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return value.quantize(
        Decimal('.{}'.format('1'.zfill(decimal_count))),
        rounding=ROUND_HALF_UP
    )


def calculate_slumber_consumption_watt() -> Optional[int]:
    """ Groups all electricity readings to find the most constant consumption. """
    most_common = ElectricityConsumption.objects.filter(
        currently_delivered__gt=0
    ).values('currently_delivered').annotate(
        currently_delivered_count=Count('currently_delivered')
    ).order_by('-currently_delivered_count')[:5]

    if not most_common:
        return None

    # We calculate the average among the most common consumption read.
    count = 0
    usage = 0

    for item in most_common:
        count += item['currently_delivered_count']
        usage += item['currently_delivered_count'] * item['currently_delivered']

    return round(usage / count * 1000)


def calculate_min_max_consumption_watt() -> Dict:
    """ Returns the lowest and highest Wattage consumed for each phase. """
    FIELDS = {
        'total_min': ('currently_delivered', ''),
        'total_max': ('currently_delivered', '-'),
        'l1_max': ('phase_currently_delivered_l1', '-'),
        'l2_max': ('phase_currently_delivered_l2', '-'),
        'l3_max': ('phase_currently_delivered_l3', '-'),
    }
    data = {}

    for name, args in FIELDS.items():
        field, sorting = args

        try:
            read_at, value = ElectricityConsumption.objects.filter(**{
                '{}__gt'.format(field): 0,  # Skip (obvious) zero values.
                '{}__isnull'.format(field): False,  # And skip empty data.
            }).order_by(
                '{}{}'.format(sorting, field)
            ).values_list('read_at', field)[0]
        except IndexError:
            continue

        data.update({
            name: (
                formats.date_format(timezone.localtime(read_at), 'DSMR_GRAPH_LONG_DATE_FORMAT'),
                int(value * 1000)
            )
        })

    return data


def clear_consumption() -> None:
    """ Clears ALL consumption data ever generated. """
    ElectricityConsumption.objects.all().delete()
    GasConsumption.objects.all().delete()


def summarize_energy_contracts() -> List[Dict]:
    """ Returns a summery of all energy contracts and some statistics along them. """
    import dsmr_stats.services  # Prevents circular import.

    data = []
    MAPPED_PRICE_FIELDS = {
        'electricity_delivered_1_price': 'electricity1_cost',
        'electricity_delivered_2_price': 'electricity2_cost',
        'gas_price': 'gas_cost',
        'fixed_daily_cost': 'fixed_cost',
    }

    for current in EnergySupplierPrice.objects.all().order_by('-start'):
        end_date = current.end or timezone.now().date()
        summary = dsmr_stats.services.range_statistics(
            start=current.start,
            # Note: +1 day is due to range_statistics()'s query (#1534)
            end=end_date + timezone.timedelta(days=1)
        )

        # Override this one, since it's only good when ALL price fields are set.
        summary['total_cost'] = Decimal(0)

        for price_field, summary_field in MAPPED_PRICE_FIELDS.items():
            if getattr(current, price_field) == 0:
                continue

            # Gas may be None/null.
            if summary[summary_field] is None:
                continue

            summary['total_cost'] += summary[summary_field]

        try:
            first_day = DayStatistics.objects.filter(
                day__gte=current.start, day__lt=current.end
            ).order_by('day')[0]
        except IndexError:
            first_day = None

        data.append({
            'description': current.description,
            'start': current.start,
            'end': current.end,
            'summary': summary,
            'prices': {
                'electricity_delivered_1_price': current.electricity_delivered_1_price,
                'electricity_delivered_2_price': current.electricity_delivered_2_price,
                'gas_price': current.gas_price,
                'electricity_returned_1_price': current.electricity_returned_1_price,
                'electricity_returned_2_price': current.electricity_returned_2_price,
                'fixed_daily_cost': current.fixed_daily_cost,
            },
            'first_day': first_day,
        })

    return data


def get_day_prices(day: datetime.date) -> EnergySupplierPrice:
    """ Returns the prices set for a day. Combines prices when multiple contracts are found. """
    contracts_found = EnergySupplierPrice.objects.filter(start__lte=day, end__gte=day)

    if len(contracts_found) == 1:
        return contracts_found[0]

    combined_contract = get_fallback_prices()

    if not contracts_found:
        raise EnergySupplierPrice.DoesNotExist()

    # Multiple found, this is allowed, as long are there is no collision.
    PRICE_FIELDS = (
        'electricity_delivered_1_price',
        'electricity_delivered_2_price',
        'gas_price',
        'electricity_returned_1_price',
        'electricity_returned_2_price',
        'fixed_daily_cost',
    )

    for current_field in PRICE_FIELDS:
        prices = [
            getattr(x, current_field) for x in contracts_found if getattr(x, current_field) > 0
        ]

        # None set.
        if not prices:
            continue

        # Collision, use none since we cannot tell which one superseeds the other.
        if len(prices) > 1:
            continue

        setattr(combined_contract, current_field, prices[0])

    return combined_contract


def get_fallback_prices() -> EnergySupplierPrice:
    # Default to zero prices.
    return EnergySupplierPrice(
        description='Zero priced contract',
        electricity_delivered_1_price=0,
        electricity_delivered_2_price=0,
        gas_price=0,
        electricity_returned_1_price=0,
        electricity_returned_2_price=0,
        fixed_daily_cost=0,
    )
