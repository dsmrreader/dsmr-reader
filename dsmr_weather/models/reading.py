from django.db import models
from django.utils.translation import gettext_lazy as _

from dsmr_backend.mixins import ModelUpdateMixin


class TemperatureReading(ModelUpdateMixin, models.Model):
    """ Hourly temperature statistics. Model is generic to isolate it from external services. """
    read_at = models.DateTimeField(unique=True)
    degrees_celcius = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_('Temperature (in ℃)'),
    )

    def __str__(self):
        return '{}: {} ℃'.format(
            self.read_at, self.degrees_celcius
        )

    class Meta:
        default_permissions = tuple()
