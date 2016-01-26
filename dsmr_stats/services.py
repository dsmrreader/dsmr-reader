from decimal import Decimal, ROUND_UP

from django.conf import settings
from django.utils import timezone
from django.db.models import Avg

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.note import Note
from dsmr_weather.models.statistics import TemperatureReading


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
    try:
        consumption['daily_energy_price'] = EnergySupplierPrice.objects.by_date(
            target_date=consumption['day']
        )
    except EnergySupplierPrice.DoesNotExist:
        # Default to zero prices.
        consumption['daily_energy_price'] = EnergySupplierPrice()

    electricity_readings = ElectricityConsumption.objects.filter(
        read_at__gte=day_start, read_at__lt=day_end,
    ).order_by('read_at')
    gas_readings = GasConsumption.objects.filter(
        read_at__gte=day_start, read_at__lt=day_end,
    ).order_by('read_at')
    temperature_readings = TemperatureReading.objects.filter(
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
    consumption['electricity1_unit_price'] = consumption['daily_energy_price'].electricity_1_price
    consumption['electricity2_unit_price'] = consumption['daily_energy_price'].electricity_2_price
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
    consumption['gas_unit_price'] = consumption['daily_energy_price'].gas_price
    consumption['gas_cost'] = round_price(
        consumption['gas'] * consumption['gas_unit_price']
    )

    consumption['total_cost'] = round_price(
        consumption['electricity1_cost'] + consumption['electricity2_cost'] + consumption['gas_cost']
    )
    consumption['notes'] = Note.objects.filter(
        day=consumption['day']
    ).values_list('description', flat=True)

    consumption['average_temperature'] = temperature_readings.aggregate(
        avg_temperature=Avg('degrees_celcius'),
    )['avg_temperature'] or 0

    return consumption


def round_price(decimal_price):
    """ Round the price to two decimals. """
    return decimal_price.quantize(Decimal('.01'), rounding=ROUND_UP)
