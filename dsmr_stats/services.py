import datetime
import re

import pytz
from django.utils import timezone

from dsmr_stats.models import DsmrReading, ElectricityConsumption, GasConsumption, ElectricityStatistics


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
    timezone = pytz.timezone("CET")
    return datetime.datetime(
        year=2000 + int(timestamp.group(1)),
        month=int(timestamp.group(2)),
        day=int(timestamp.group(3)),
        hour=int(timestamp.group(4)),
        minute=int(timestamp.group(5)),
        second=int(timestamp.group(6)),
        tzinfo=timezone
    )


def compact(dsmr_reading):
    # Electricity should be unique, because it's the reading
    # with the lowest interval anyway.
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
