from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class MQTTBrokerSettings(ModelUpdateMixin, SingletonModel):
    """ MQTT broker connection. """
    INSECURE = 0
    SECURE_CERT_NONE = 1
    SECURE_CERT_REQUIRED = 2
    SECURE_CHOICES = (
        (INSECURE, _('INSECURE - No SSL/TLS')),
        (SECURE_CERT_NONE, _('SECURE (CERT_NONE) - Validation errors are ignored (untrusted or expired certficates)')),
        (SECURE_CERT_REQUIRED, _('SECURE (CERT_REQUIRED) - Requires a valid/trusted certificate')),
    )

    QOS_0 = 0
    QOS_1 = 1
    QOS_2 = 2
    QOS_CHOICES = (
        (QOS_0, 'QoS 0 - At most once (default)'),
        (QOS_1, 'QoS 1 - At least once'),
        (QOS_2, 'QoS 2 - Exactly once'),
    )

    hostname = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Hostname'),
        help_text=_('The hostname of the broker to send MQTT messages to.')
    )
    port = models.IntegerField(
        null=True,
        default=1883,
        verbose_name=_('Port'),
        help_text=_('MQTT: 1883 - MQTTS: 8883')
    )
    secure = models.IntegerField(
        default=INSECURE,
        choices=SECURE_CHOICES,
        verbose_name=_('Secure (SSL/TLS)'),
        help_text=_(
            'Whether the client should use a secure connection. '
            'Select SECURE (CERT_NONE) for self-signed certificates. '
            'Make sure to use the appropriate MQTT(S) port as well.'
        )
    )
    username = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Username'),
        help_text=_('Optional: The username required for authentication (if any).')
    )
    password = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Password'),
        help_text=_('Optional: The password required for authentication (if any).')
    )
    client_id = models.CharField(
        max_length=256,
        default='DSMR-reader',
        verbose_name=_('Client ID'),
        help_text=_('The client ID used to identify DSMR-reader sending the MQTT messages.')
    )
    qos = models.IntegerField(
        default=QOS_0,
        choices=QOS_CHOICES,
        verbose_name=_('Quality Of Service'),
        help_text=_(
            'QoS 0: Fastest performance, but unreliable (designed for reliable connections, such as cabled networks). '
            'QoS 1: Average performance, but reliable. Caveat: May re-send messages, causing them to duplicate! '
            'QoS 2: Slowest performance, but reliable and prevents sending duplicate messages.'
        )
    )
    restart_required = models.BooleanField(
        default=False,
        verbose_name=_('Restart required'),
        help_text=_('Whether the process requires a restart, forcing the client-broker connection to be reset.')
    )
    process_sleep = models.DecimalField(
        default=1,
        max_digits=3,
        decimal_places=1,
        verbose_name=_('MQTT process sleep'),
        help_text=_(
            'The number of seconds the application will sleep after publishing the outgoing MQTT message queue.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT Broker/connection')
