from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import requests

from dsmr_notification.models.settings import NotificationSetting
from dsmr_consumption.models.consumption import GasConsumption
from dsmr_stats.models import DayStatistics


def should_notify():
    """ Checks whether we should notify """
    settings = NotificationSetting.get_solo()
    return settings.send_notification or False


def notify():
    """ Exports readings and costs for notifications. """
    if not should_notify():
        return

    # Just post the latest reading of the day before.
    today = timezone.localtime(timezone.now())
    midnight = timezone.make_aware(timezone.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=0,
    ))

    try:
        stats = DayStatistics.objects.get(
            day=(midnight - timezone.timedelta(hours=1))
        )
    except IndexError:
        raise AssertionError('Push-notification failed: no data')

    settings = NotificationSetting.get_solo()

    notification_api_url = NotificationSetting.NOTIFICATION_API_URL.get(
        settings.notification_service)

    message = _('Your daily usage statics for {}\n'
                'Total cost: € {}\n'
                'Electricity: {} kWh\n'
                'Gas: {} m3').format(
        (midnight - timezone.timedelta(hours=1)).strftime("%d-%m-%Y"),
        stats.total_cost,
        (float(stats.electricity1)+float(stats.electricity2)),
        stats.gas
    )

    # Send API by
    response = requests.post(notification_api_url, {
        'apikey': settings.api_key,
        'priority': '-2',
        'application': 'DSMR-Reader',
        'event': str(_('Daily usage notification')),
        'description': message
    })

    if response.status_code != 200:
        raise AssertionError('Push-notification failed: %s (HTTP%s)'.format(
            response.text, response.status_code))
