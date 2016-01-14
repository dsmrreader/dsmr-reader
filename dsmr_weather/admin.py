from django.contrib import admin
from solo.admin import SingletonModelAdmin


from dsmr_weather.models.statistics import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings


@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    list_display = ('read_at', 'temperature_celcius')


@admin.register(WeatherSettings)
class WeatherSettingsAdmin(SingletonModelAdmin):
    list_display = ('track', 'buienradar_station')
