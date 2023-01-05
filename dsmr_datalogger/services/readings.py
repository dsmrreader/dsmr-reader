import datetime

from django.utils import timezone

from dsmr_backend.dto import Capability
from dsmr_datalogger.dto import MeterPositionsDTO
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_backend.services.backend


def first_meter_positions_of_day(day: datetime.date) -> MeterPositionsDTO:
    """
    Returns the first meter positions of the given day, when available.
    Raises LookupError when nothing matched.
    """
    hours_in_day = dsmr_backend.services.backend.hours_in_day(day=day)
    start_of_day = timezone.make_aware(
        timezone.datetime(year=day.year, month=day.month, day=day.day, hour=0, minute=0)
    )
    end_of_day = start_of_day + timezone.timedelta(hours=hours_in_day)

    first_electricity_reading_of_day = (
        DsmrReading.objects.filter(
            timestamp__gte=start_of_day,
            timestamp__lt=end_of_day,
        )
        .order_by("timestamp")
        .first()
    )

    if not first_electricity_reading_of_day:
        raise LookupError()

    if dsmr_backend.services.backend.get_capability(Capability.GAS):
        # Gas readings may lag a bit behind for DSMR v4 telegrams. Make sure the gas meter updated the timestamp!
        first_gas_reading_of_day = (
            DsmrReading.objects.filter(
                # DB indexed
                timestamp__gte=start_of_day,
                timestamp__lt=end_of_day,
                # No DB index
                extra_device_timestamp__gte=start_of_day,
                extra_device_timestamp__lt=end_of_day,
            )
            .order_by("extra_device_timestamp")
            .first()
        )
    else:
        first_gas_reading_of_day = None

    return MeterPositionsDTO(
        electricity_timestamp=first_electricity_reading_of_day.timestamp,
        electricity_delivered_1=first_electricity_reading_of_day.electricity_delivered_1,
        electricity_returned_1=first_electricity_reading_of_day.electricity_returned_1,
        electricity_delivered_2=first_electricity_reading_of_day.electricity_delivered_2,
        electricity_returned_2=first_electricity_reading_of_day.electricity_returned_2,
        extra_device_timestamp=first_gas_reading_of_day.extra_device_timestamp
        if first_gas_reading_of_day
        else None,
        extra_device_delivered=first_gas_reading_of_day.extra_device_delivered
        if first_gas_reading_of_day
        else None,
    )
