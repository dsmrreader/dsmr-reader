from django.contrib import admin
from solo.admin import SingletonModelAdmin

from dsmr_weather.models.settings import WeatherSettings


@admin.register(WeatherSettings)
class WeatherSettingsAdmin(SingletonModelAdmin):
    list_display = ('track', 'buienradar_station')
