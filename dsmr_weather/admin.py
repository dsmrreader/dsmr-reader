from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from dsmr_weather.models.settings import WeatherSettings


@admin.register(WeatherSettings)
class WeatherSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('next_sync', )
    fieldsets = (
        (
            None, {
                'fields': ['track'],
            }
        ),
        (
            _('Buienradar'), {
                'fields': ['buienradar_station'],
                'description': _(
                    'See <a href="https://www.buienradar.nl/nederland/weerbericht/weerstations" target="_blank">'
                    'Buienradar weerstations</a> for a map of all locations.')
            }
        ),
        (
            _('Automatic fields'), {
                'fields': ['next_sync']
            }
        ),
    )
