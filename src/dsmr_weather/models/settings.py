from typing import ClassVar
from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


def _buienradar_station_choices() -> list[tuple[int, str]]:
    from dsmr_weather.services import get_buienradar_stations

    return get_buienradar_stations()


class WeatherSettings(ModelUpdateMixin, SingletonModel):
    track = models.BooleanField(  # type: ignore[var-annotated]
        default=False,
        verbose_name=_("Track weather"),
        help_text=_(
            "Whether we should track and log outside temperatures using an external service. "
            "Current service integrated is Buienradar"
        ),
    )
    buienradar_station = models.IntegerField(  # type: ignore[var-annotated]
        choices=_buienradar_station_choices,
        default=6260,  # "De Bilt"
        verbose_name=_("Buienradar weather station"),
        help_text=_("The weather station used to measure and log outside temperatures. Choose one nearby."),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions: ClassVar[tuple[str, ...]] = tuple()
        verbose_name = _("Weather configuration")
