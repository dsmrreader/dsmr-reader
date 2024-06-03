import logging
from typing import Optional, Dict

from django.conf import settings
from django.utils import timezone
import requests

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings, PVOutputAPISettings
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_pvoutput.signals import pvoutput_upload


logger = logging.getLogger("dsmrreader")


def run(scheduled_process: ScheduledProcess) -> None:
    """Exports data to PVOutput, calling Add Status."""
    api_settings = PVOutputAPISettings.get_solo()
    status_settings = PVOutputAddStatusSettings.get_solo()

    # Only when enabled and credentials set.
    if (
        not status_settings.export
        or not api_settings.auth_token
        or not api_settings.system_identifier
    ):
        logger.error("PVOutput: Export disabled or no auth token/system ID set")
        scheduled_process.disable()
        return

    try:
        data = get_export_data(
            next_export=scheduled_process.planned,
            upload_delay=status_settings.upload_delay,
        )
    except LookupError:
        return

    if not data:
        logger.warning("PVOutput: No data found (yet)")
        schedule_next_export(scheduled_process)
        return

    # Optional paid feature in PVOutput.
    if status_settings.processing_delay:
        data.update(dict(delay=status_settings.processing_delay))

    logger.debug("PVOutput: Pre-upload data signal")
    pvoutput_upload.send_robust(None, data=data)

    logger.debug("PVOutput: Uploading data: %s", data)
    response = requests.post(
        PVOutputAddStatusSettings.API_URL,
        headers={
            "User-Agent": settings.DSMRREADER_USER_AGENT,
            "X-Pvoutput-Apikey": api_settings.auth_token,
            "X-Pvoutput-SystemId": api_settings.system_identifier,
        },
        data=data,
        timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
    )

    if response.status_code != 200:
        logger.error(
            "PVOutput: Upload failed (HTTP %s): %s", response.status_code, response.text
        )
        scheduled_process.delay(minutes=5)
        return

    schedule_next_export(scheduled_process)


def schedule_next_export(scheduled_process: ScheduledProcess) -> None:
    """Schedules the next export, according to user preference."""
    next_export = get_next_export()

    logger.debug(
        "PVOutput:  Delaying the next export until: %s", timezone.localtime(next_export)
    )
    scheduled_process.reschedule(next_export)


def get_next_export() -> timezone.datetime:
    """Rounds the timestamp to the nearest upload interval, preventing the uploads to shift forward."""
    upload_interval = PVOutputAddStatusSettings.get_solo().upload_interval

    next_export = timezone.now() + timezone.timedelta(minutes=upload_interval)

    # Make sure it shifts back to the closest interval point possible.
    minute_marker = next_export.minute
    minute_marker = minute_marker - (minute_marker % upload_interval)

    return next_export.replace(minute=minute_marker, second=0, microsecond=0)


def get_export_data(
    next_export: Optional[timezone.datetime], upload_delay: int
) -> Optional[Dict]:
    """Returns the data to export. Raises exception when 'not ready'."""
    # Find the first and last consumption of today, taking any delay into account.
    local_now = timezone.localtime(timezone.now())
    search_start = local_now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )  # Midnight
    search_end = local_now - timezone.timedelta(minutes=upload_delay)

    ecs = ElectricityConsumption.objects.filter(
        read_at__gte=search_start, read_at__lte=search_end
    )

    if not ecs.exists():
        return None

    first = ecs[0]
    last = ecs.order_by("-read_at")[0]
    consumption_timestamp = timezone.localtime(last.read_at)

    # Check whether we need to delay the export, until we have data that untill at least the current upload time. (#467)
    if next_export is not None:
        expected_data_timestamp = timezone.localtime(
            next_export - timezone.timedelta(minutes=upload_delay)
        )

        if consumption_timestamp < expected_data_timestamp:
            logger.warning(
                "PVOutput: Data found, but not in sync. Last data timestamp is before expected (%s < %s)",
                consumption_timestamp,
                expected_data_timestamp,
            )
            raise LookupError()

    diff = last - first  # Custom operator for convenience
    total_consumption = diff["delivered_1"] + diff["delivered_2"]
    net_power = last.currently_delivered - last.currently_returned

    return dict(
        d=consumption_timestamp.date().strftime("%Y%m%d"),
        t=consumption_timestamp.time().strftime("%H:%M"),
        # Energy Consumption (Wh).
        v3=int(total_consumption * 1000),
        # Power Consumption (W). Negative value when returning more Watt than consumed in your household.
        v4=int(net_power * 1000),
        # Net Flag. Always enabled for smart meters!
        n=1,
    )
