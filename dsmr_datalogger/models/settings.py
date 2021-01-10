from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel
import django.db.models.signals

from dsmr_backend.mixins import ModelUpdateMixin
from dsmr_datalogger.signals import datalogger_restart_required


class DataloggerSettings(ModelUpdateMixin, SingletonModel):
    INPUT_METHOD_SERIAL = 'serial'
    INPUT_METHOD_IPV4 = 'ipv4'
    INPUT_METHODS = (
        (INPUT_METHOD_SERIAL, _('Serial port')),
        (INPUT_METHOD_IPV4, _('Network socket (IPv4)')),
    )

    DSMR_VERSION_4_PLUS = 4
    DSMR_VERSION_2_3 = 3
    DSMR_BELGIUM_FLUVIUS = 101
    DSMR_LUXEMBOURG_SMARTY = 102
    DSMR_VERSION_CHOICES = (
        (DSMR_VERSION_4_PLUS, _('Netherlands - DSMR version 4/5 (default)')),
        (DSMR_VERSION_2_3, _('Netherlands - DSMR version 2/3')),
        (DSMR_BELGIUM_FLUVIUS, _('Belgium - Fluvius (gas meter fix)')),
        (DSMR_LUXEMBOURG_SMARTY, _('Luxembourg - Smarty (single tariff fix)')),
    )

    input_method = models.CharField(
        max_length=16,
        default=INPUT_METHOD_SERIAL,
        choices=INPUT_METHODS,
        verbose_name=_('Input method'),
        help_text=_('Whether to read telegrams from a serial port or network socket.')
    )
    dsmr_version = models.IntegerField(
        default=DSMR_VERSION_4_PLUS,
        choices=DSMR_VERSION_CHOICES,
        verbose_name=_('DSMR version'),
        help_text=_('The DSMR version your meter supports. Version should be printed on meter.')
    )
    serial_port = models.CharField(
        max_length=196,
        default='/dev/ttyUSB0',
        blank=True,
        null=True,
        verbose_name=_('Serial port'),
        help_text=_('For serial input: Serial port connected to smartmeter. E.g.: /dev/ttyUSB0')
    )
    network_socket_address = models.CharField(
        max_length=196,
        default=None,
        blank=True,
        null=True,
        verbose_name=_('Network socket address'),
        help_text=_('For network input: IP address or hostname of the network device connected to smartmeter.')
    )
    network_socket_port = models.IntegerField(
        default=23,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name=_('Network socket port'),
        help_text=_('For network input: Port of the network device connected to smartmeter.')
    )
    process_sleep = models.DecimalField(
        default=5.0,
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.5), MaxValueValidator(99)],
        verbose_name=_('Datalogger process sleep'),
        help_text=_(
            'The number of seconds the application will sleep after reading data from the datalogger (API excluded).'
        )
    )
    restart_required = models.BooleanField(
        default=False,
        verbose_name=_('Process restart required'),
        help_text=_('Whether the datalogger process requires a restart. It should occur automatically.')
    )
    override_telegram_timestamp = models.BooleanField(
        default=False,
        verbose_name=_('Override telegram timestamp'),
        help_text=_(
            'Whether DSMR-reader should IGNORE any timestamps of incoming telegrams and use the current timestamp '
            'instead. Use with care and only when your situation actually requires this!'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Datalogger configuration')


@receiver(django.db.models.signals.post_save, sender=DataloggerSettings)
def _on_datalogger_settings_updated_signal(instance, created, raw, **kwargs):
    """ On settings change, require datalogger restart. """
    if created or raw:
        return

    datalogger_restart_required.send_robust(None)


@receiver(datalogger_restart_required)
def _on_datalogger_restart_required_signal(**kwargs):
    # Do not use save() here due to infinite looping.
    DataloggerSettings.objects.update(restart_required=True)


class RetentionSettings(ModelUpdateMixin, SingletonModel):
    RETENTION_NONE = None
    RETENTION_WEEK = 7 * 24
    RETENTION_MONTH = 4 * RETENTION_WEEK
    RETENTION_THREE_MONTHS = 3 * RETENTION_MONTH
    RETENTION_HALF_YEAR = 6 * RETENTION_MONTH
    RETENTION_YEAR = 12 * RETENTION_MONTH
    RETENTION_CHOICES = (
        (RETENTION_NONE, _('Disabled (WARNING: Will eventually lead to performance issues!)')),
        (RETENTION_WEEK, _('Clean up most source data after one week (RECOMMENDED)')),
        (RETENTION_MONTH, _('Clean up most source data after one month (RECOMMENDED)')),
        (RETENTION_THREE_MONTHS, _('Clean up most source data after three months')),
        (RETENTION_HALF_YEAR, _('Clean up most source data after six months')),
        (RETENTION_YEAR, _('Clean up most source data after one year')),
    )

    data_retention_in_hours = models.IntegerField(
        blank=True,
        null=True,
        default=RETENTION_MONTH,
        choices=RETENTION_CHOICES,
        verbose_name=_('Data retention policy'),
        help_text=_(
            'The lifetime of source readings and consumption records. Day and hour statistics will always be preserved '
            'indefinitely.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Retention configuration')
