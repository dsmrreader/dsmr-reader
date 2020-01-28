from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class ConsumptionSettings(ModelUpdateMixin, SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    ELECTRICITY_GROUPING_BY_READING = 1
    ELECTRICITY_GROUPING_BY_MINUTE = 2
    ELECTRICITY_GROUPING_CHOICES = (
        (ELECTRICITY_GROUPING_BY_READING, _('By reading (default)')),
        (ELECTRICITY_GROUPING_BY_MINUTE, _('By minute')),
    )
    GAS_GROUPING_BY_CHANGE = 1
    GAS_GROUPING_BY_HOUR = 2
    GAS_GROUPING_CHOICES = (
        (GAS_GROUPING_BY_CHANGE, _('On every change (default)')),
        (GAS_GROUPING_BY_HOUR, _('Force grouping by hour')),
    )

    electricity_grouping_type = models.IntegerField(
        choices=ELECTRICITY_GROUPING_CHOICES,
        default=ELECTRICITY_GROUPING_BY_MINUTE,
        verbose_name=_('Electricity grouping type'),
        help_text=_(
            'Electricity readings are read every X seconds, depending on your meter. We can group these for you.'
        )
    )
    gas_grouping_type = models.IntegerField(
        choices=GAS_GROUPING_CHOICES,
        default=GAS_GROUPING_BY_CHANGE,
        verbose_name=_('Gas grouping type'),
        help_text=_(
            'DSMR 4 (gas) meters always group readings by hour. DSMR 5 (gas) meters can be optionally grouped by hour.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Consumption configuration')
