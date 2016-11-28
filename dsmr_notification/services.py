import requests
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dsmr_notification.models.settings import NotificationSetting
from dsmr_stats.models.statistics import DayStatistics
import dsmr_consumption.services
import dsmr_backend.services


def should_notify(settings):
    """ Checks whether we should notify
    :param settings:
    """

    # Only when enabled and token set.
    if not settings.send_notification or not settings.api_key:
        return False

    # Only when it's time..
    if settings.next_notification is not None \
            and timezone.localtime(timezone.now()).date() < settings.next_notification:
        return False

    return True


def get_notification_api_url(settings):
    """ Retrieve the API url for the notification service
    :param settings:
    """
    return NotificationSetting.NOTIFICATION_API_URL[
        settings.notification_service]


def get_notification_priority():
    """ Get the priority indicator for the notification API's
    :return:
    """
    return '-2'


def get_notification_sender_name():
    """ Get the sender name for the notification API's
    :return:
    """
    return 'DSMR-Reader'


def get_notification_event_name():
    """ Get the event name for the notification API's
    :return:
    """
    return str(_('Daily usage notification'))


def create_notification_message(day, stats):
    """
    Create the action notification message
    :param day:
    :param stats:
    :return:
    """
    capabilities = dsmr_backend.services.get_capabilities()
    day_date = (day - timezone.timedelta(hours=1)).strftime("%d-%m-%Y")
    message = _('Your daily usage statistics for {}\n').format(day_date)

    if capabilities['electricity']:
        electricity_merged = dsmr_consumption.services.round_decimal(stats.electricity_merged)
        message += _('Electricity consumed: {} kWh\n').format(electricity_merged)

    if capabilities['electricity_returned']:
        electricity_returned_merged = dsmr_consumption.services.round_decimal(stats.electricity_returned_merged)
        message += _('Electricity returned: {} kWh\n').format(electricity_returned_merged)

    if capabilities['gas']:
        gas = dsmr_consumption.services.round_decimal(stats.gas)
        message += _('Gas consumed: {} m3\n').format(gas)

    message += _('Total cost: € {}').format(dsmr_consumption.services.round_decimal(stats.total_cost))
    return message


def send_notification(api_url, api_key, notification_message):
    """ Sends notification using the preferred service
    :param api_url:
    :param api_key:
    :param notification_message:
    """
    response = requests.post(api_url, {
        'apikey': api_key,
        'priority': get_notification_priority(),
        'application': get_notification_sender_name(),
        'event': get_notification_event_name(),
        'description': notification_message
    })

    if response.status_code != 200:
        raise AssertionError('Notify API call failed: {0} (HTTP{1})'.format(
            response.text, response.status_code))

    return True


def set_next_notification(settings, now):
    """ Set the next moment for notifications to be allowed again
    :param now:
    :param settings:
    """
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
        notification_api_url = get_notification_api_url(settings)
    except KeyError:
        raise AssertionError('Could not determine notification API url!')

    try:
        stats = DayStatistics.objects.get(
            day=(midnight - timezone.timedelta(hours=1))
        )
    except DayStatistics.DoesNotExist:
        return False  # Try again in a next run

    message = create_notification_message(midnight, stats)
    send_notification(notification_api_url, settings.api_key, message)
    set_next_notification(settings, today)
