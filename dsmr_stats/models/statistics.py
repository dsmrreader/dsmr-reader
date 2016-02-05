from django.db import models


class DayStatistics(models.Model):
    """ Daily consumption usage summary. """
    day = models.DateField(unique=True)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)

    electricity1 = models.DecimalField(max_digits=9, decimal_places=3)
    electricity2 = models.DecimalField(max_digits=9, decimal_places=3)
    electricity1_returned = models.DecimalField(max_digits=9, decimal_places=3)
    electricity2_returned = models.DecimalField(max_digits=9, decimal_places=3)
    electricity1_cost = models.DecimalField(max_digits=8, decimal_places=2)
    electricity2_cost = models.DecimalField(max_digits=8, decimal_places=2)

    # Gas readings are optional/not guaranteed.
    gas = models.DecimalField(max_digits=9, decimal_places=3, null=True, default=None)
    gas_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)

    # Temperature readings depend on user settings.
    average_temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, default=None
    )

    class Meta:
        default_permissions = tuple()
