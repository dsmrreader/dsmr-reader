from datetime import time
import re

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Max

from dsmr_stats.models import DsmrReading, ElectricityConsumption, GasConsumption, \
    ElectricityStatistics, EnergySupplierPrice
from decimal import Decimal, ROUND_UP
import pytz


def telegram_to_reading(data):
    """
    Converts a P1 telegram to a DSMR reading, stored in database.
    """
    reading = {}
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
            reading[field[0]] = reading_timestamp_to_datetime(string=timestamp_value)
            reading[field[1]] = gas_usage
        else:
            if field == "timestamp":
                value = reading_timestamp_to_datetime(string=value)

            reading[field] = value

    return DsmrReading.objects.create(**reading)


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


@transaction.atomic
def compact(dsmr_reading, group_by_minute=False):
    """
    Compacts/converts DSMR readings to consumption data. Optionally groups electricity by minute.
    """
    # Electricity should be unique, because it's the reading with the lowest interval anyway.
    if not group_by_minute:
        ElectricityConsumption.objects.create(
            read_at=dsmr_reading.timestamp,
            delivered_1=dsmr_reading.electricity_delivered_1,
            returned_1=dsmr_reading.electricity_returned_1,
            delivered_2=dsmr_reading.electricity_delivered_2,
            returned_2=dsmr_reading.electricity_returned_2,
            tariff=dsmr_reading.electricity_tariff,
            currently_delivered=dsmr_reading.electricity_currently_delivered,
            currently_returned=dsmr_reading.electricity_currently_returned,
        )
    # Grouping by minute requires some distinction and history checking.
    else:
        minute_start = timezone.datetime.combine(
            dsmr_reading.timestamp.date(),
            time(hour=dsmr_reading.timestamp.hour, minute=dsmr_reading.timestamp.minute),
        ).replace(tzinfo=pytz.UTC)
        minute_end = minute_start + timezone.timedelta(minutes=1)

        # We might have six readings per minute, so there is a chance we already parsed it.
        # Also, delay when the minute hasn't passed yet. 
        if not ElectricityConsumption.objects.filter(read_at=minute_end).exists() and \
                timezone.now() > minute_end:
            grouped_reading = DsmrReading.objects.filter(
                timestamp__gte=minute_start, timestamp__lt=minute_end
            ).aggregate(
                avg_delivered=Avg('electricity_currently_delivered'),
                avg_returned=Avg('electricity_currently_returned'),
                max_delivered_1=Max('electricity_delivered_1'),
                max_delivered_2=Max('electricity_delivered_2'),
                max_returned_1=Max('electricity_returned_1'),
                max_returned_2=Max('electricity_returned_2')
            )

            # This instance is the average/max and combined result.
            ElectricityConsumption.objects.create(
                read_at=minute_end,
                delivered_1=grouped_reading['max_delivered_1'],
                returned_1=grouped_reading['max_returned_1'],
                delivered_2=grouped_reading['max_delivered_2'],
                returned_2=grouped_reading['max_returned_2'],
                tariff=dsmr_reading.electricity_tariff,
                currently_delivered=grouped_reading['avg_delivered'],
                currently_returned=grouped_reading['avg_returned'],
            )

    # Gas however only get read every hour, so we should check
    # for any duplicates, as they WILL exist.
    gas_consumption_exists = GasConsumption.objects.filter(
        read_at=dsmr_reading.extra_device_timestamp
    ).exists()

    if not gas_consumption_exists:
        # DSMR does not expose current gas rate, so we have to calculate
        # it ourselves, relative to the previous gas consumption, if any.
        try:
            previous_gas_consumption = GasConsumption.objects.get(
                read_at=dsmr_reading.extra_device_timestamp - timezone.timedelta(hours=1)
            )
        except GasConsumption.DoesNotExist:
            gas_diff = 0
        else:
            gas_diff = dsmr_reading.extra_device_delivered - previous_gas_consumption.delivered

        GasConsumption.objects.create(
            read_at=dsmr_reading.extra_device_timestamp,
            delivered=dsmr_reading.extra_device_delivered,
            currently_delivered=gas_diff
        )

    # The last thing to do is to keep track of other daily statistics.
    electricity_statistics = ElectricityStatistics(
        day=dsmr_reading.timestamp.date(),
        power_failure_count=dsmr_reading.power_failure_count,
        long_power_failure_count=dsmr_reading.long_power_failure_count,
        voltage_sag_count_l1=dsmr_reading.voltage_sag_count_l1,
        voltage_sag_count_l2=dsmr_reading.voltage_sag_count_l2,
        voltage_sag_count_l3=dsmr_reading.voltage_sag_count_l3,
        voltage_swell_count_l1=dsmr_reading.voltage_swell_count_l1,
        voltage_swell_count_l2=dsmr_reading.voltage_swell_count_l2,
        voltage_swell_count_l3=dsmr_reading.voltage_swell_count_l3,
    )

    try:
        existing_statistics = ElectricityStatistics.objects.get(
            day=electricity_statistics.day
        )
    except:
        electricity_statistics.save()
    else:
        # Already exists, but only save if dirty.
        if not existing_statistics.is_equal(electricity_statistics):
            electricity_statistics.id = existing_statistics.id
            electricity_statistics.pk = existing_statistics.pk
            electricity_statistics.save()

    dsmr_reading.processed = True
    dsmr_reading.save(update_fields=['processed'])


def day_consumption(day):
    consumption = {'day': day.date()}
    day_start = timezone.datetime(
        year=day.year,
        month=day.month,
        day=day.day,
        tzinfo=settings.LOCAL_TIME_ZONE
    )
    day_end = day_start + timezone.timedelta(days=1)

    # This WILL fail when we either have no prices at all or conflicting ranges.
    daily_energy_price = EnergySupplierPrice.objects.by_date(
        target_date=consumption['day']
    )

    electricity_readings = ElectricityConsumption.objects.filter(
        read_at__gte=day_start, read_at__lt=day_end,
    ).order_by('read_at')
    gas_readings = GasConsumption.objects.filter(
        read_at__gte=day_start, read_at__lt=day_end,
    ).order_by('read_at')

    if not electricity_readings.exists() or not gas_readings.exists():
        raise LookupError("No readings found for: {}".format(day.date()))

    electricity_reading_count = electricity_readings.count()
    gas_reading_count = gas_readings.count()

    first_reading = electricity_readings[0]
    last_reading = electricity_readings[electricity_reading_count - 1]
    consumption['electricity1'] = last_reading.delivered_1 - first_reading.delivered_1
    consumption['electricity2'] = last_reading.delivered_2 - first_reading.delivered_2
    consumption['electricity1_returned'] = last_reading.returned_1 - first_reading.returned_1
    consumption['electricity2_returned'] = last_reading.returned_2 - first_reading.returned_2
    consumption['electricity1_start'] = first_reading.delivered_1
    consumption['electricity1_end'] = last_reading.delivered_1
    consumption['electricity2_start'] = first_reading.delivered_2
    consumption['electricity2_end'] = last_reading.delivered_2
    consumption['electricity1_unit_price'] = daily_energy_price.electricity_1_price
    consumption['electricity2_unit_price'] = daily_energy_price.electricity_2_price
    consumption['electricity1_cost'] = round_price(
        consumption['electricity1'] * consumption['electricity1_unit_price']
    )
    consumption['electricity2_cost'] = round_price(
        consumption['electricity2'] * consumption['electricity2_unit_price']
    )

    first_reading = gas_readings[0]
    last_reading = gas_readings[gas_reading_count - 1]
    consumption['gas'] = last_reading.delivered - first_reading.delivered
    consumption['gas_start'] = first_reading.delivered
    consumption['gas_end'] = last_reading.delivered
    consumption['gas_unit_price'] = daily_energy_price.gas_price
    consumption['gas_cost'] = round_price(
        consumption['gas'] * consumption['gas_unit_price']
    )

    consumption['total_cost'] = round_price(
        consumption['electricity1_cost'] + consumption['electricity2_cost'] + consumption['gas_cost']
    )

    return consumption


def round_price(decimal_price):
    return decimal_price.quantize(Decimal('.01'), rounding=ROUND_UP)
