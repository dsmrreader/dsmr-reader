from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class DataloggerSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    DSMR_VERSION_4_PLUS = 4
    DSMR_VERSION_2 = 3  # Yes that is a three and it's legacy.
    DSMR_VERSION_CHOICES = (
        (DSMR_VERSION_4_PLUS, _('DSMR version 4+')),
        (DSMR_VERSION_2, _('DSMR version 2')),
    )

    track = models.BooleanField(
        default=True,
        verbose_name=_('Poll P1 port'),
        help_text=_(
            'Whether we should track the P1 port on your smartmeter. Almost every feature inside '
            'this project requires this to be enabled. However, it might be disabled temporarily '
            'due to technical reasons, such as data migrations.'
        )
    )
    track_phases = models.BooleanField(
        default=False,
        verbose_name=_('Track electricity phases'),
        help_text=_(
            'Whether we should track your phases (if any) as well. By default you only have one phase, but some meters '
            'have three due to solar panels or an electric stove. This feature is only useful (and will only work) '
            'when actually you have three phases. The dashboard will display any data read, after enabling this.'
        )
    )
    verify_telegram_crc = models.BooleanField(
        default=True,
        verbose_name=_('Verify telegram CRC'),
        help_text=_('Whether we should verify the CRC of any telegrams read by / sent to the application.')
    )

    dsmr_version = models.IntegerField(
        default=DSMR_VERSION_4_PLUS,
        choices=DSMR_VERSION_CHOICES,
        verbose_name=_('DSMR version'),
        help_text=_('The DSMR version your meter supports. Version should be printed on meter.')
    )
    com_port = models.CharField(
        max_length=196,
        default='/dev/ttyUSB0',
        verbose_name=_('COM-port'),
        help_text=_('COM-port connected to Smartmeter.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Datalogger configuration')


class RetentionSettings(SingletonModel):
    RETENTION_NONE = None
    RETENTION_WEEK = 7 * 24
    RETENTION_MONTH = 4 * RETENTION_WEEK
    RETENTION_HALF_YEAR = 6 * RETENTION_MONTH
    RETENTION_YEAR = 12 * RETENTION_MONTH
    RETENTION_CHOICES = (
        (RETENTION_NONE, _('None (keep all readings)')),
        (RETENTION_WEEK, _('Discard most readings after one week')),
        (RETENTION_MONTH, _('Discard most readings after one month')),
        (RETENTION_HALF_YEAR, _('Discard most readings after six months')),
        (RETENTION_YEAR, _('Discard most readings after one year')),
    )

    data_retention_in_hours = models.IntegerField(
        blank=True,
        null=True,
        default=RETENTION_NONE,
        choices=RETENTION_CHOICES,
        verbose_name=_('Data retention'),
        help_text=_(
            'The lifetime of readings, before discarding them. Please note that retention is applied during night time '
            'currently, between midnight and six in the morning.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Retention configuration')
