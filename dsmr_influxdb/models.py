from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class InfluxdbIntegrationSettings(ModelUpdateMixin, SingletonModel):
    INSECURE = 'insecure'
    SECURE_CERT_NONE = 'secure_no_verify'
    SECURE_CERT_REQUIRED = 'secure_and_verify'
    SECURE_CHOICES = (
        (INSECURE, _('INSECURE - No HTTPS (default)')),
        (SECURE_CERT_NONE, _('SECURE (CERT_NONE) - HTTPS, but errors are ignored (untrusted or expired certificates)')),
        (SECURE_CERT_REQUIRED, _('SECURE (CERT_REQUIRED) - HTTPS and requires a valid/trusted certificate')),
    )

    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether the InfluxDB integration is enabled.')
    )
    hostname = models.CharField(
        max_length=128,
        default='localhost',
        verbose_name=_('InfluxDB hostname'),
        help_text=_('The hostname of the InfluxDB.')
    )
    port = models.IntegerField(
        default=8086,
        verbose_name=_('InfluxDB port'),
        help_text=_('Default: 8086')
    )
    database = models.CharField(
        max_length=64,
        verbose_name=_('InfluxDB database'),
        help_text=_('The name of the database used in InfluxDB.')
    )
    username = models.CharField(
        blank=True,
        max_length=64,
        verbose_name=_('InfluxDB username'),
        help_text=_('Optional: The username used for authentication with InfluxDB.')
    )
    password = models.CharField(
        blank=True,
        max_length=64,
        verbose_name=_('InfluxDB password'),
        help_text=_('Optional: The password used for authentication with InfluxDB.')
    )
    secure = models.CharField(
        max_length=24,
        default=INSECURE,
        choices=SECURE_CHOICES,
        verbose_name=_('Use secure connection (HTTPS)'),
        help_text=_(
            'Whether the client should use a secure connection. '
            'Select SECURE (CERT_NONE) for self-signed certificates. '
        )
    )
    formatting = models.TextField(
        default='''
### [measurement_name]
### DSMR-reader field 1 = InfluxDB field 1
### DSMR-reader field 2 = InfluxDB field 2

[electricity_live]
electricity_currently_delivered = currently_delivered
electricity_currently_returned = currently_returned

[electricity_positions]
electricity_delivered_1 = delivered_1
electricity_returned_1 = returned_1
electricity_delivered_2 = delivered_2
electricity_returned_2 = returned_2

[electricity_voltage]
phase_voltage_l1 = phase_l1
phase_voltage_l2 = phase_l2
phase_voltage_l3 = phase_l3

[electricity_phases]
phase_currently_delivered_l1 = currently_delivered_l1
phase_currently_delivered_l2 = currently_delivered_l2
phase_currently_delivered_l3 = currently_delivered_l3
phase_currently_returned_l1 = currently_returned_l1
phase_currently_returned_l2 = currently_returned_l2
phase_currently_returned_l3 = currently_returned_l3

[electricity_power]
phase_power_current_l1 = current_l1
phase_power_current_l2 = current_l2
phase_power_current_l3 = current_l3

[gas_positions]
extra_device_delivered = delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Mapping used for the measurements used in your InfluxDB database.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('InfluxDB integration')


class InfluxdbMeasurement(ModelUpdateMixin, models.Model):
    """ Queued measurement for InfluxDB. """
    time = models.DateTimeField()
    measurement_name = models.CharField(max_length=255)
    fields = models.TextField()

    def __str__(self):
        return self.measurement_name

    class Meta:
        default_permissions = ('delete', )  # Do allow deletion.
        verbose_name = _('Influxdb measurement')
        verbose_name_plural = _('Influxdb measurements')
