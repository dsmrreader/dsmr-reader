from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class JSONCurrentPeriodTotalsMQTTSettings(ModelUpdateMixin, SingletonModel):
    """ Daily update of current month and year totals. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether the period totals are sent to the broker, in JSON format.')
    )
    topic = models.CharField(
        max_length=256,
        default='dsmr/current-period',
        verbose_name=_('Topic path'),
        help_text=_('The topic to send the JSON formatted message to.')
    )
    formatting = models.TextField(
        default='''
[mapping]
### SOURCE DATA = JSON FIELD
### Only alter fields on the RIGHT HAND SIDE below. Remove lines to omit them from the JSON structure sent.

### Current month
current_month_electricity1 = current_month_electricity1
current_month_electricity2 = current_month_electricity2
current_month_electricity1_returned = current_month_electricity1_returned
current_month_electricity2_returned = current_month_electricity2_returned
current_month_electricity_merged = current_month_electricity_merged
current_month_electricity_returned_merged = current_month_electricity_returned_merged
current_month_electricity1_cost = current_month_electricity1_cost
current_month_electricity2_cost = current_month_electricity2_cost
current_month_electricity_cost_merged = current_month_electricity_cost_merged
current_month_gas = current_month_gas
current_month_gas_cost = current_month_gas_cost
current_month_fixed_cost = current_month_fixed_cost
current_month_total_cost = current_month_total_cost

### Current year
current_year_electricity1 = current_year_electricity1
current_year_electricity2 = current_year_electricity2
current_year_electricity1_returned = current_year_electricity1_returned
current_year_electricity2_returned = current_year_electricity2_returned
current_year_electricity_merged = current_year_electricity_merged
current_year_electricity_returned_merged = current_year_electricity_returned_merged
current_year_electricity1_cost = current_year_electricity1_cost
current_year_electricity2_cost = current_year_electricity2_cost
current_year_electricity_cost_merged = current_year_electricity_cost_merged
current_year_gas = current_year_gas
current_year_gas_cost = current_year_gas_cost
current_year_fixed_cost = current_year_fixed_cost
current_year_total_cost = current_year_total_cost
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names used in the JSON message sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Current month/year totals: JSON')


class SplitTopicCurrentPeriodTotalsMQTTSettings(ModelUpdateMixin, SingletonModel):
    """ Daily update of current month and year totals. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether period totals are sent to the broker, having each field sent to a different topic.')
    )
    formatting = models.TextField(
        default='''
[mapping]
### SOURCE DATA = TOPIC PATH
### Only alter the topic paths on the RIGHT HAND SIDE below. Remove lines to prevent them from being sent at all.

### Current month
current_month_electricity1 = dsmr/current-month/electricity1
current_month_electricity2 = dsmr/current-month/electricity2
current_month_electricity1_returned = dsmr/current-month/electricity1_returned
current_month_electricity2_returned = dsmr/current-month/electricity2_returned
current_month_electricity_merged = dsmr/current-month/electricity_merged
current_month_electricity_returned_merged = dsmr/current-month/electricity_returned_merged
current_month_electricity1_cost = dsmr/current-month/electricity1_cost
current_month_electricity2_cost = dsmr/current-month/electricity2_cost
current_month_electricity_cost_merged = dsmr/current-month/electricity_cost_merged
current_month_gas = dsmr/current-month/gas
current_month_gas_cost = dsmr/current-month/gas_cost
current_month_fixed_cost = dsmr/current-month/fixed_cost
current_month_total_cost = dsmr/current-month/total_cost

### Current year
current_year_electricity1 = dsmr/current-year/electricity1
current_year_electricity2 = dsmr/current-year/electricity2
current_year_electricity1_returned = dsmr/current-year/electricity1_returned
current_year_electricity2_returned = dsmr/current-year/electricity2_returned
current_year_electricity_merged = dsmr/current-year/electricity_merged
current_year_electricity_returned_merged = dsmr/current-year/electricity_returned_merged
current_year_electricity1_cost = dsmr/current-year/electricity1_cost
current_year_electricity2_cost = dsmr/current-year/electricity2_cost
current_year_electricity_cost_merged = dsmr/current-year/electricity_cost_merged
current_year_gas = dsmr/current-year/gas
current_year_gas_cost = dsmr/current-year/gas_cost
current_year_fixed_cost = dsmr/current-year/fixed_cost
current_year_total_cost = dsmr/current-year/total_cost
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names to separate topics sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Current month/year totals: Split topic')
