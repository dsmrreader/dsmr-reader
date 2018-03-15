from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import requests

from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting
from dsmr_stats.models.statistics import DayStatistics
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_consumption.services
import dsmr_backend.services


def should_notify():
    """ Checks whether we should notify """
    settings = NotificationSetting.get_solo()

    # Only when enabled and token set.
    if settings.notification_service is None or not settings.api_key:
        return False

    # Only when it's time.
    if settings.next_notification is not None \
            and timezone.localtime(timezone.now()).date() < settings.next_notification:
        return False

    return True


def create_notification_message(day, stats):
    """ Create the action notification message """
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


def send_notification(api_url, api_key, notification_message, title):
    """ Sends notification using the preferred service """
    response = requests.post(api_url, {
        'apikey': api_key,
        'priority': '-2',
        'application': 'DSMR-Reader',
        'event': title,
        'description': notification_message
    })

    if response.status_code != 200:
        raise AssertionError('Notify API call failed: {0} (HTTP{1})'.format(response.text, response.status_code))

    return True


def set_next_notification(settings, now):
    """ Set the next moment for notifications to be allowed again """
    tomorrow = (now + timezone.timedelta(hours=24)).date()
    settings.next_notification = tomorrow
    settings.save()


def notify():
    """ Sends notifications about daily energy usage """
    settings = NotificationSetting.get_solo()

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

    notification_api_url = NotificationSetting.NOTIFICATION_API_URL[settings.notification_service]

    try:
        stats = DayStatistics.objects.get(
            day=(midnight - timezone.timedelta(hours=1))
        )
    except DayStatistics.DoesNotExist:
        return False  # Try again in a next run

    # For backend logging in Supervisor.
    print(' - Creating new notification containing daily usage.')

    message = create_notification_message(midnight, stats)
    send_notification(notification_api_url, settings.api_key, message, str(_('Daily usage notification')))
    set_next_notification(settings, today)


def check_status():
    """ Checks the status of the application. """
    status_settings = StatusNotificationSetting.get_solo()

    if not dsmr_backend.services.is_timestamp_passed(timestamp=status_settings.next_check):
        return

    # Check for recent data.
    has_recent_reading = DsmrReading.objects.filter(
        timestamp__gt=timezone.now() - timezone.timedelta(minutes=settings.DSMRREADER_STATUS_READING_OFFSET_MINUTES)
    ).exists()

    if has_recent_reading:
        return

    # Alert!

    StatusNotificationSetting.objects.update(
        next_check=timezone.now() + settings.DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS
    )
