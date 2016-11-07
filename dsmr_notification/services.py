import requests

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dsmr_notification.models.settings import NotificationSetting
from dsmr_stats.models import DayStatistics


def should_notify(settings):
    """ Checks whether we should notify """

    # Only when enabled and token set.
    if not settings.send_notification or not settings.api_key:
        return False

    # Only when it's time..
    if settings.next_notification is not None \
            and timezone.localtime(timezone.now()).date() < settings.next_notification:
        return False

    return True


def send_notification(api_url, api_key, notification_message):
    """ Sends notification using the preferred service  """

    response = requests.post(api_url, {
        'apikey': api_key,
        'priority': '-2',
        'application': 'DSMR-Reader',
        'event': str(_('Daily usage notification')),
        'description': notification_message
    })

    if response.status_code != 200:
        raise AssertionError('Push-notification failed: %s (HTTP%s)'.format(
            response.text, response.status_code))

    return True


def set_next_notification(settings, now):
    """ Set the next moment for notifications to be allowed again """
    tomorrow = (now + timezone.timedelta(hours=24)).date()
    settings.next_notification = tomorrow
    settings.save()


def notify():
    """ Sends notifications about daily energy usage """
    settings = NotificationSetting.get_solo()

    if not should_notify(settings):
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
    except DayStatistics.DoesNotExist:
        return  # Try again some other time



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

    send_notification(notification_api_url, settings.api_key, message)
    set_next_notification(settings, today)