from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

from dsmr_weather.buienradar import BUIENRADAR_STATIONS


class WeatherSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    track = models.BooleanField(
        default=False,
        verbose_name=_('Track weather'),
        help_text=_(
            'Whether we should track and log outside temperatures using an external service. '
            'Current service integrated is Buienradar'
        )
    )
    buienradar_station = models.IntegerField(
        choices=BUIENRADAR_STATIONS,
        default=6260,  # "De Bilt"
        verbose_name=_('Buienradar weather station'),
        help_text=_(
            'The weather station used to measure and log outside temperatures. Choose one nearby. '
            'See http://www.buienradar.nl/weerkaarten/temperatuur for a map of all locations.'
        )
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Weather configuration')
