from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class WeatherSettings(ModelUpdateMixin, SingletonModel):
    BUIENRADAR_STATIONS = (
        (6391, _("Weather station Arcen")),
        (6275, _("Weather station Arnhem")),
        (6249, _("Weather station Berkhout")),
        (6308, _("Weather station Cadzand")),
        (6260, _("Weather station De Bilt")),
        (6235, _("Weather station Den Helder")),
        (6370, _("Weather station Eindhoven")),
        (6377, _("Weather station Ell")),
        (6321, _("Weather station Euro platform")),
        (6350, _("Weather station Gilze Rijen")),
        (6283, _("Weather station Groenlo-Hupsel")),
        (6280, _("Weather station Groningen")),
        (6315, _("Weather station Hansweert")),
        (6278, _("Weather station Heino")),
        (6356, _("Weather station Herwijnen")),
        (6330, _("Weather station Hoek van Holland")),
        (6311, _("Weather station Hoofdplaat")),
        (6279, _("Weather station Hoogeveen")),
        (6251, _("Weather station Hoorn Terschelling")),
        (6258, _("Weather station Houtribdijk")),
        (6285, _("Weather station Huibertgat")),
        (6209, _("Weather station IJmond")),
        (6225, _("Weather station IJmuiden")),
        (6210, _("Weather station Katwijk")),
        (6277, _("Weather station Lauwersoog")),
        (6320, _("Weather station LE Goeree")),
        (6270, _("Weather station Leeuwarden")),
        (6269, _("Weather station Lelystad")),
        (6348, _("Weather station Lopik-Cabauw")),
        (6380, _("Weather station Maastricht")),
        (6273, _("Weather station Marknesse")),
        (6286, _("Weather station Nieuw Beerta")),
        (6312, _("Weather station Oosterschelde")),
        (6344, _("Weather station Rotterdam")),
        (6343, _("Weather station Rotterdam Geulhaven")),
        (6316, _("Weather station Schaar")),
        (6240, _("Weather station Schiphol")),
        (6324, _("Weather station Stavenisse")),
        (6267, _("Weather station Stavoren")),
        (6331, _("Weather station Tholen")),
        (6290, _("Weather station Twente")),
        (6313, _("Weather station Vlakte aan de Raan")),
        (6242, _("Weather station Vlieland")),
        (6310, _("Weather station Vlissingen")),
        (6375, _("Weather station Volkel")),
        (6215, _("Weather station Voorschoten")),
        (6319, _("Weather station Westdorpe")),
        (6248, _("Weather station Wijdenes")),
        (6257, _("Weather station Wijk aan Zee")),
        (6340, _("Weather station Woensdrecht")),
        (6239, _("Weather station Zeeplatform F-3")),
        (6252, _("Weather station Zeeplatform K13")),
    )

    track = models.BooleanField(
        default=False,
        verbose_name=_("Track weather"),
        help_text=_(
            "Whether we should track and log outside temperatures using an external service. "
            "Current service integrated is Buienradar"
        ),
    )
    buienradar_station = models.IntegerField(
        choices=BUIENRADAR_STATIONS,
        default=6260,  # "De Bilt"
        verbose_name=_("Buienradar weather station"),
        help_text=_(
            "The weather station used to measure and log outside temperatures. Choose one nearby."
        ),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _("Weather configuration")
