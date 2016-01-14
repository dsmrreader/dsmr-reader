from dsmr_weather.models.settings import WeatherSettings


def read_weather():
    """ Reads the current weather state. """
    # Only when explicitly enabled in settings.
    weather_settings = WeatherSettings.get_solo()

    if not weather_settings.track:
        return
