from django.db import models
from django.utils.translation import ugettext_lazy as _


class DayStatistics(models.Model):
    """ Daily consumption usage summary. """
    day = models.DateField(unique=True, db_index=True, verbose_name=_('Date'))
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Total cost'))

    electricity1 = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 1 (low tariff)')
    )
    electricity2 = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 2 (high tariff)')
    )
    electricity1_returned = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 1 returned (low tariff)')
    )
    electricity2_returned = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 2 returned (high tariff)')
    )
    electricity1_cost = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_('Electricity 1 price (low tariff)')
    )
    electricity2_cost = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_('Electricity 2 price (high tariff)')
    )

    # Gas readings are optional/not guaranteed.
    gas = models.DecimalField(
        max_digits=9, decimal_places=3, null=True, default=None, verbose_name=_('Gas')
    )
    gas_cost = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, default=None, verbose_name=_('Gas price')
    )

    # Temperature readings depend on user settings.
    lowest_temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, default=None, verbose_name=_('Lowest temperature')
    )
    highest_temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, default=None, verbose_name=_('Highest temperature')
    )
    average_temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, default=None, verbose_name=_('Average temperature')
    )

    @property
    def electricity_merged(self):
        return self.electricity1 + self.electricity2

    @property
    def electricity_returned_merged(self):
        return self.electricity1_returned + self.electricity2_returned

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Day statistics (automatically generated data)')
        verbose_name_plural = verbose_name
        ordering = ['day']

    def __str__(self):
        return '{}: {}'.format(
            self.__class__.__name__, self.day
        )


class HourStatistics(models.Model):
    """ Hourly consumption usage summary. """
    hour_start = models.DateTimeField(unique=True, db_index=True, verbose_name=_('Hour start'))

    electricity1 = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 1 (low tariff)')
    )
    electricity2 = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 2 (high tariff)')
    )
    electricity1_returned = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 1 returned (low tariff)')
    )
    electricity2_returned = models.DecimalField(
        max_digits=9, decimal_places=3, verbose_name=_('Electricity 2 returned (high tariff)')
    )

    # Gas readings are optional/not guaranteed. But need to be zero due to averages.
    gas = models.DecimalField(max_digits=9, decimal_places=3, default=0, verbose_name=_('Gas'))

    @property
    def electricity_merged(self):
        return self.electricity1 + self.electricity2

    @property
    def electricity_returned_merged(self):
        return self.electricity1_returned + self.electricity2_returned

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Hour statistics (automatically generated data)')
        verbose_name_plural = verbose_name
        ordering = ['hour_start']

    def __str__(self):
        return '{}: {}'.format(
            self.__class__.__name__, self.hour_start
        )
