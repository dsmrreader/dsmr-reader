from django.utils import timezone
import requests

from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings, PVOutputAPISettings
from dsmr_consumption.models.consumption import ElectricityConsumption
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
    status_settings = PVOutputAddStatusSettings.get_solo()

    next_export = timezone.now() + timezone.timedelta(minutes=status_settings.upload_interval)
    print(' - PVOutput | Delaying the next export until: {}'.format(next_export))

    status_settings.next_export = next_export
    status_settings.save()


def export():
    """ Exports data to PVOutput, calling Add Status. """
    if not should_export():
        return

    api_settings = PVOutputAPISettings.get_solo()
    status_settings = PVOutputAddStatusSettings.get_solo()

    # Find the first and last consumption of today, taking any delay into account.
    local_now = timezone.localtime(timezone.now())
    start = local_now.replace(hour=0, minute=0, second=0)  # Midnight
    end = local_now - timezone.timedelta(minutes=status_settings.upload_delay)

    ecs = ElectricityConsumption.objects.filter(read_at__gte=start, read_at__lte=end)

    if not ecs.exists():
        print(' [!] PVOutput: No data found for {}'.format(local_now))
        return schedule_next_export()

    first = ecs[0]
    last = ecs.order_by('-read_at')[0]
    diff = last - first  # Custom operator

    total_consumption = diff['delivered_1'] + diff['delivered_2']
    net_power = last.currently_delivered - last.currently_returned  # Negative when returning more Watt than requested.

    consumption_timestamp = timezone.localtime(last.read_at)

    data = {
        'd': consumption_timestamp.date().strftime('%Y%m%d'),
        't': consumption_timestamp.time().strftime('%H:%M'),
        'v3': int(total_consumption * 1000),  # Energy Consumption (Wh)
        'v4': int(net_power * 1000),  # Power Consumption (W)
        'n': 1,  # Net Flag, always enabled for smart meters
    }

    # Optional, paid PVOutput feature.
    if status_settings.processing_delay:
        data.update({'delay': status_settings.processing_delay})

    print(' - PVOutput | Uploading data @ {}'.format(data['t']))
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

    schedule_next_export()
