from django.utils.translation import gettext_lazy as _
from django.db import models
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class JSONGasConsumptionMQTTSettings(ModelUpdateMixin, SingletonModel):
    """ MQTT JSON gas consumption. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether gas consumption is sent to the broker, in JSON format.')
    )
    topic = models.CharField(
        max_length=256,
        default='dsmr/consumption/gas/json',
        verbose_name=_('Topic path'),
        help_text=_('The topic to send the parsed JSON telegrams to.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# DATA FIELD = JSON FIELD
read_at = read_at
delivered = delivered
currently_delivered = currently_delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names used in the JSON message sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Gas consumption: JSON')


class SplitTopicGasConsumptionMQTTSettings(ModelUpdateMixin, SingletonModel):
    """ MQTT splitted gas consumption per field, mapped to topics. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether gas consumption is sent to the broker, having each field sent to a different topic.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# READING FIELD = TOPIC PATH
read_at = dsmr/consumption/gas/read_at
delivered = dsmr/consumption/gas/delivered
currently_delivered = dsmr/consumption/gas/currently_delivered
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names to separate topics sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Gas consumption: Split topic')
