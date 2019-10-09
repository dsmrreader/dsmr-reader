from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models
from solo.models import SingletonModel


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
        verbose_name = _('(Data source) Telegram: Raw')


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
phase_currently_returned_l1 = phase_currently_returned_l1
phase_currently_returned_l2 = phase_currently_returned_l2
phase_currently_returned_l3 = phase_currently_returned_l3
extra_device_timestamp = extra_device_timestamp
extra_device_delivered = extra_device_delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names used in the JSON message sent to the broker.')
    )
    use_local_timezone = models.BooleanField(
        default=False,
        verbose_name=_('Use local timezone'),
        help_text=_('Whether to use the local timezone ({}) in the timestamp sent.'.format(
            settings.TIME_ZONE
        ))
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Telegram: JSON')


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
phase_currently_returned_l1 = dsmr/reading/phase_currently_returned_l1
phase_currently_returned_l2 = dsmr/reading/phase_currently_returned_l2
phase_currently_returned_l3 = dsmr/reading/phase_currently_returned_l3
extra_device_timestamp = dsmr/reading/extra_device_timestamp
extra_device_delivered = dsmr/reading/extra_device_delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names to separate topics sent to the broker.')
    )
    use_local_timezone = models.BooleanField(
        default=False,
        verbose_name=_('Use local timezone'),
        help_text=_('Whether to use the local timezone ({}) in the timestamp sent.'.format(
            settings.TIME_ZONE
        ))
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Telegram: Split topic')
