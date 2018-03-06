from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class MQTTBrokerSettings(SingletonModel):
    """ MQTT broker connection. """
    hostname = models.CharField(
        max_length=256,
        null=True,
        default=None,
        verbose_name=_('Hostname'),
        help_text=_('The hostname of the broker to send MQTT messages to.')
    )
    port = models.IntegerField(
        null=True,
        default=1883,
        verbose_name=_('Port'),
        help_text=_('The port of the broker to send MQTT messages to.')
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

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT broker configuration')
