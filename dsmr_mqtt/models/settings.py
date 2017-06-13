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


class RawTelegramMQTTSettings(SingletonModel):
    """ MQTT raw telegrams. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether any raw telegrams received are sent to the broker.')
    )
    topic = models.CharField(
        max_length=256,
        default='dsmr/raw',
        verbose_name=_('Topic path'),
        help_text=_('The topic to send the raw telegrams to.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT raw telegram configuration')


class JSONTelegramMQTTSettings(SingletonModel):
    """ MQTT JSON telegram. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether parsed telegrams are sent to the broker, in JSON format.')
    )
    topic = models.CharField(
        max_length=256,
        default='dsmr/json',
        verbose_name=_('Topic path'),
        help_text=_('The topic to send the parsed JSON telegrams to.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# READING FIELD = JSON FIELD
id = id
timestamp = timestamp
electricity_delivered_1 = electricity_delivered_1
electricity_returned_1 = electricity_returned_1
electricity_delivered_2 = electricity_delivered_2
electricity_returned_2 = electricity_returned_2
electricity_currently_delivered = electricity_currently_delivered
electricity_currently_returned = electricity_currently_returned
phase_currently_delivered_l1 = phase_currently_delivered_l1
phase_currently_delivered_l2 = phase_currently_delivered_l2
phase_currently_delivered_l3 = phase_currently_delivered_l3
extra_device_timestamp = extra_device_timestamp
extra_device_delivered = extra_device_delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names used in the JSON message sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT JSON telegram configuration')


class SplitTopicTelegramMQTTSettings(SingletonModel):
    """ MQTT splitted telegram per field, mapped to topics. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether parsed telegrams are sent to the broker, having each field sent to a different topic.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# READING FIELD = TOPIC PATH
id = dsmr/reading/id
timestamp = dsmr/reading/timestamp
electricity_delivered_1 = dsmr/reading/electricity_delivered_1
electricity_returned_1 = dsmr/reading/electricity_returned_1
electricity_delivered_2 = dsmr/reading/electricity_delivered_2
electricity_returned_2 = dsmr/reading/electricity_returned_2
electricity_currently_delivered = dsmr/reading/electricity_currently_delivered
electricity_currently_returned = dsmr/reading/electricity_currently_returned
phase_currently_delivered_l1 = dsmr/reading/phase_currently_delivered_l1
phase_currently_delivered_l2 = dsmr/reading/phase_currently_delivered_l2
phase_currently_delivered_l3 = dsmr/reading/phase_currently_delivered_l3
extra_device_timestamp = dsmr/reading/extra_device_timestamp
extra_device_delivered = dsmr/reading/extra_device_delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names to separate topics sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT split topic telegram configuration')
