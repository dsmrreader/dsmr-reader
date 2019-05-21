import logging

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, translation
from django.conf import settings
import requests

from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting
from dsmr_backend.models.settings import BackendSettings, EmailSettings
from dsmr_stats.models.statistics import DayStatistics
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_frontend.models.message import Notification
import dsmr_consumption.services
import dsmr_backend.services.backend
import dsmr_backend.services.email


logger = logging.getLogger('commands')


def notify_pre_check():
    """ Checks whether we should notify """
    notification_settings = NotificationSetting.get_solo()

    if notification_settings.notification_service is None:
        return False

    # Dummy message?
    if notification_settings.next_notification is None:
        send_notification(
            message='DSMR-reader notification test.',
            title='DSMR-reader Test Notification'
        )
        NotificationSetting.objects.update(next_notification=timezone.now())
        return True

    # Ready to go, but not time yet.
    if notification_settings.next_notification is not None and timezone.now() < notification_settings.next_notification:
        return False

    return True


def create_consumption_message(day, stats):
    """ Create the action notification message """
    capabilities = dsmr_backend.services.backend.get_capabilities()
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


def send_notification(message, title):
    """ Sends notification using the preferred service """
    notification_settings = NotificationSetting.get_solo()

    DATA_FORMAT = {
        NotificationSetting.NOTIFICATION_PUSHOVER: {
            'url': NotificationSetting.PUSHOVER_API_URL,
            'data': {
                'token': notification_settings.pushover_api_key,
                'user': notification_settings.pushover_user_key,
                'priority': '-1',
                'title': title,
                'message': message
            }
        },
        NotificationSetting.NOTIFICATION_PROWL: {
            'url': NotificationSetting.PROWL_API_URL,
            'data': {
                'apikey': notification_settings.prowl_api_key,
                'priority': '-2',
                'application': 'DSMR-Reader',
                'event': title,
                'description': message
            }
        },
        NotificationSetting.NOTIFICATION_TELEGRAM: {
            'url': '{}{}/sendMessage'.format(
                NotificationSetting.TELEGRAM_API_URL, notification_settings.telegram_api_key
            ),
            'data': {
                'chat_id': notification_settings.telegram_chat_id,
                'disable_notification': 'true',
                'text': message
            }
        },
    }

    if notification_settings.notification_service == NotificationSetting.NOTIFICATION_EMAIL:
        email_settings = EmailSettings.get_solo()
        dsmr_backend.services.email.send(
            to=email_settings.email_to,
            subject=title,
            body=message,
        )
        return

    response = requests.post(
        **DATA_FORMAT[notification_settings.notification_service]
    )

    if response.status_code == 200:
        return

    # Invalid request, do not retry.
    if str(response.status_code).startswith('4'):
        logger.error(' - Notification API returned client error, wiping settings...')
        NotificationSetting.objects.update(
            notification_service=None,
            pushover_api_key=None,
            pushover_user_key=None,
            prowl_api_key=None,
            next_notification=None,
            telegram_api_key=None,
            telegram_chat_id=None
        )
        Notification.objects.create(
            message='Notification API error, settings are reset. Error: {}'.format(response.text),
            redirect_to='admin:dsmr_notification_notificationsetting_changelist'
        )

    # Server error, delay a bit.
    elif str(response.status_code).startswith('5'):
        logger.warning(' - Notification API returned server error, retrying later...')
        NotificationSetting.objects.update(
            next_notification=timezone.now() + timezone.timedelta(minutes=5)
        )

    raise AssertionError('Notify API call failed: {0} (HTTP {1})'.format(response.text, response.status_code))


def set_next_notification():
    """ Set the next moment for notifications to be allowed again """
    DAILY_NOTIFICATION_HOUR = 6

    # DST can cause some trouble. We need to go forward and set the requested hour.
    next_notification = timezone.now() + timezone.timedelta(hours=24)
    next_notification = next_notification.replace(hour=DAILY_NOTIFICATION_HOUR, minute=0, second=0, microsecond=0)

    # Now we recalculate our new timezone. This only changes twice a year due to DST.
    next_notification = timezone.localtime(next_notification)

    # And we have to replace the hour, again. Prevents sending notifications an hour early or late on the next day.
    next_notification = next_notification.replace(hour=DAILY_NOTIFICATION_HOUR, minute=0, second=0, microsecond=0)

    NotificationSetting.objects.update(next_notification=next_notification)


def notify():
    """ Sends notifications about daily energy usage """
    if not notify_pre_check():
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
        return  # Try again in a next run

    # For backend logging in Supervisor.
    logger.debug(' - Creating new notification containing daily usage.')

    with translation.override(language=BackendSettings.get_solo().language):
        message = create_consumption_message(midnight, stats)
        send_notification(message, str(_('Daily usage notification')))

    set_next_notification()


def check_status():
    """ Checks the status of the application. """
    status_settings = StatusNotificationSetting.get_solo()
    notification_settings = NotificationSetting.get_solo()

    if notification_settings.notification_service is None or \
            not dsmr_backend.services.backend.is_timestamp_passed(timestamp=status_settings.next_check):
        return

    if not DsmrReading.objects.exists():
        return StatusNotificationSetting.objects.update(
            next_check=timezone.now() + timezone.timedelta(minutes=5)
        )

    # Check for recent data.
    has_recent_reading = DsmrReading.objects.filter(
        timestamp__gt=timezone.now() - timezone.timedelta(minutes=settings.DSMRREADER_STATUS_READING_OFFSET_MINUTES)
    ).exists()

    if has_recent_reading:
        return StatusNotificationSetting.objects.update(
            next_check=timezone.now() + timezone.timedelta(minutes=5)
        )

    # Alert!
    logger.debug(' - Sending notification about datalogger lagging behind...')

    with translation.override(language=BackendSettings.get_solo().language):
        send_notification(
            str(_('It has been over {} hour(s) since the last reading received. Please check your datalogger.'.format(
                settings.DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS
            ))),
            str(_('Datalogger check'))
        )

    StatusNotificationSetting.objects.update(
        next_check=timezone.now() + timezone.timedelta(hours=settings.DSMRREADER_STATUS_NOTIFICATION_COOLDOWN_HOURS)
    )
