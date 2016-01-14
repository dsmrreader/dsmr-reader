from django.db import models
from django.utils.translation import ugettext as _


class TemperatureReading(models.Model):
    """ Hourly temperature statistics. Model is generic to isolate it from external services. """
    read_at = models.DateTimeField(unique=True)
    temperature_celcius = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name=_('Temperature (℃)'),
    )
