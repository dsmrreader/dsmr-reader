from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings


def get_data_capabilities():
    """
    Returns the capabilities of the data tracked, such as whether the meter supports gas readings or
    if there have been any readings regarding electricity being returned.
    """
    capabilities = {
        # We rely on consumption because DSMR readings might be flushed in the future.
        'electricity': ElectricityConsumption.objects.exists(),
        'electricity_returned': ElectricityConsumption.objects.filter(
            # We can not rely on meter positions, as the manufacturer sometimes initializes meters
            # with testing data. So we just have to wait for the first power returned.
            currently_returned__gt=0
        ).exists(),
        'gas': GasConsumption.objects.exists(),
        'weather': WeatherSettings.get_solo().track and TemperatureReading.objects.exists()
    }
    capabilities['any'] = any(capabilities.values())

    return capabilities
