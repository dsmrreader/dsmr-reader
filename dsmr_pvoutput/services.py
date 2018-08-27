from django.utils import timezone
import requests

from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings, PVOutputAPISettings
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_pvoutput.signals import pvoutput_upload
import dsmr_backend.services


def should_export():
    """ Checks whether we should export data yet, for Add Status calls. """
    api_settings = PVOutputAPISettings.get_solo()
    status_settings = PVOutputAddStatusSettings.get_solo()

    # Only when enabled and credentials set.
    if not status_settings.export or not api_settings.auth_token or not api_settings.system_identifier:
        return False

    return dsmr_backend.services.is_timestamp_passed(timestamp=status_settings.next_export)


def schedule_next_export():
    """ Schedules the next export, according to user preference. """
    next_export = get_next_export()
    print(' - PVOutput | Delaying the next export until: {}'.format(next_export))

    status_settings = PVOutputAddStatusSettings.get_solo()
    status_settings.next_export = next_export
    status_settings.save()


def get_next_export():
    """ Rounds the timestamp to the nearest upload interval, preventing the uploads to shift forward. """
    status_settings = PVOutputAddStatusSettings.get_solo()

    next_export = timezone.now() + timezone.timedelta(minutes=status_settings.upload_interval)

    # Make sure it shifts back to the closest interval point possible.
    minute_marker = next_export.minute
    minute_marker = minute_marker - (minute_marker % status_settings.upload_interval)

    return next_export.replace(minute=minute_marker, second=0, microsecond=0)


def get_export_data(next_export, upload_delay):
    """ Returns the data to export. Raises exception when 'not ready'. """
    # Find the first and last consumption of today, taking any delay into account.
    local_now = timezone.localtime(timezone.now())
    search_start = local_now.replace(hour=0, minute=0, second=0)  # Midnight
    search_end = local_now - timezone.timedelta(minutes=upload_delay)

    ecs = ElectricityConsumption.objects.filter(read_at__gte=search_start, read_at__lte=search_end)

    if not ecs.exists():
        return None

    first = ecs[0]
    last = ecs.order_by('-read_at')[0]
    consumption_timestamp = timezone.localtime(last.read_at)

    if next_export is None:
        # This should only happen once, on the first upload ever.
        next_export = timezone.localtime(timezone.now())
    else:
        # Delay the export, until we have data that reaches at least the current upload time. (#467)
        expected_data_timestamp = timezone.localtime(next_export - timezone.timedelta(minutes=upload_delay))

        if consumption_timestamp < expected_data_timestamp:
            print(' [i] PVOutput: Data found, not in sync. Last data timestamp < expected ({} < {})'.format(
                consumption_timestamp, expected_data_timestamp
            ))
            raise LookupError()

    diff = last - first  # Custom operator for convenience
    total_consumption = diff['delivered_1'] + diff['delivered_2']
    net_power = last.currently_delivered - last.currently_returned  # Negative when returning more Watt than requested.

    return {
        'd': consumption_timestamp.date().strftime('%Y%m%d'),
        't': consumption_timestamp.time().strftime('%H:%M'),
        'v3': int(total_consumption * 1000),  # Energy Consumption (Wh)
        'v4': int(net_power * 1000),  # Power Consumption (W)
        'n': 1,  # Net Flag, always enabled for smart meters
    }


def export():
    """ Exports data to PVOutput, calling Add Status. """
    if not should_export():
        return

    api_settings = PVOutputAPISettings.get_solo()
    status_settings = PVOutputAddStatusSettings.get_solo()

    try:
        data = get_export_data(next_export=status_settings.next_export, upload_delay=status_settings.upload_delay)
    except LookupError:
        return

    if not data:
        print(' [!] PVOutput: No data found (yet)')
        return schedule_next_export()

    # Optional, paid PVOutput feature.
    if status_settings.processing_delay:
        data.update({'delay': status_settings.processing_delay})

    print(' - PVOutput | Uploading data: {}'.format(data))
    pvoutput_upload.send_robust(None, data=data)

    response = requests.post(
        PVOutputAddStatusSettings.API_URL,
        headers={
            'X-Pvoutput-Apikey': api_settings.auth_token,
            'X-Pvoutput-SystemId': api_settings.system_identifier,
        },
        data=data
    )

    if response.status_code != 200:
        print(' [!] PVOutput upload failed (HTTP {}): {}'.format(response.status_code, response.text))
    else:
        status_settings.latest_sync = timezone.now()
        status_settings.save()

    schedule_next_export()
