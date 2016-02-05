from django.db import models


class ElectricityStatistics(models.Model):
    """ Daily electricity usage summary. """
    day = models.DateField(unique=True)
    electricity1 = models.DecimalField(max_digits=9, decimal_places=3)
    electricity2 = models.DecimalField(max_digits=9, decimal_places=3)
    electricity1_returned = models.DecimalField(max_digits=9, decimal_places=3)
    electricity2_returned = models.DecimalField(max_digits=9, decimal_places=3)
    electricity1_cost = models.DecimalField(max_digits=8, decimal_places=2)
    electricity2_cost = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        default_permissions = tuple()


class GasStatistics(models.Model):
    """ Daily gas usage summary. """
    day = models.DateField(unique=True)
    gas = models.DecimalField(max_digits=9, decimal_places=3)
    gas_cost = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        default_permissions = tuple()
