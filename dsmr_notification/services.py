from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import requests

from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting
from dsmr_stats.models.statistics import DayStatistics
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_backend.exceptions import DelayNextCall
import dsmr_consumption.services
import dsmr_backend.services


def should_notify():
    """ Checks whether we should notify """
    notification_settings = NotificationSetting.get_solo()

    # Only when enabled and token set.
    if notification_settings.notification_service is None or not notification_settings.api_key:
        return False

    # Only when it's time.
    if notification_settings.next_notification is not None \
            and timezone.localtime(timezone.now()).date() < notification_settings.next_notification:
        return False

    return True


def create_consumption_notification_message(day, stats):
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


def notify():
    """ Sends notifications about daily energy usage """
    notification_settings = NotificationSetting.get_solo()

    if not should_notify():
        raise DelayNextCall(minutes=1)

    # Just post the latest reading of the day before.
    today = timezone.localtime(timezone.now())
    midnight = timezone.make_aware(timezone.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=0,
    ))

    notification_api_url = NotificationSetting.NOTIFICATION_API_URL[notification_settings.notification_service]

    try:
        stats = DayStatistics.objects.get(
            day=(midnight - timezone.timedelta(hours=1))
        )
    except DayStatistics.DoesNotExist:
        # Try again in a next run
        raise DelayNextCall(hours=1)

    # For backend logging in Supervisor.
    print(' - Creating new notification containing daily usage.')

    message = create_consumption_notification_message(midnight, stats)
    send_notification(notification_api_url, notification_settings.api_key, message, str(_('Daily usage notification')))

    tomorrow = (today + timezone.timedelta(hours=24)).date()
    NotificationSetting.objects.update(next_notification=tomorrow)

    next_call = timezone.make_aware(timezone.datetime.combine(tomorrow, timezone.datetime.min.time()))
    raise DelayNextCall(timestamp=next_call)


def check_status():
    """ Checks the status of the application. """
    status_settings = StatusNotificationSetting.get_solo()
    notification_settings = NotificationSetting.get_solo()

    if notification_settings.notification_service is None or \
            not dsmr_backend.services.is_timestamp_passed(timestamp=status_settings.next_check):
        raise DelayNextCall(minutes=1)

    if not DsmrReading.objects.exists():
        StatusNotificationSetting.objects.update(
            next_check=timezone.now() + timezone.timedelta(minutes=5)
        )
        raise DelayNextCall(minutes=5)

    # Check for recent data.
    has_recent_reading = DsmrReading.objects.filter(
        timestamp__gt=timezone.now() - timezone.timedelta(minutes=settings.DSMRREADER_STATUS_READING_OFFSET_MINUTES)
    ).exists()

    if has_recent_reading:
        StatusNotificationSetting.objects.update(
            next_check=timezone.now() + timezone.timedelta(minutes=5)
        )
        raise DelayNextCall(minutes=5)

    # Alert!
    print(' - Sending notification about datalogger lagging behind...')
    send_notification(
        NotificationSetting.NOTIFICATION_API_URL[notification_settings.notification_service],
        notification_settings.api_key,
        str(_('It has been over an hour since the last reading received. Please check your datalogger.')),
        str(_('Datalogger check'))
    )

    next_check = timezone.now() + timezone.timedelta(hours=settings.DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS)
    StatusNotificationSetting.objects.update(next_check=next_check)

    raise DelayNextCall(timestamp=next_check)
