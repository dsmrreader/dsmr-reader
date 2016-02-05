from collections import defaultdict
import json

from django.conf import settings
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.statistics import DayStatistics
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
import dsmr_consumption.services


class DashboardMixin(object):
    electricity_max = 60
    gas_max = 3 * 24
    temperature_max = gas_max

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()
        context_data = super(DashboardMixin, self).get_context_data(**kwargs)

        electricity = ElectricityConsumption.objects.all().order_by('read_at')
        gas = GasConsumption.objects.all().order_by('read_at')
        temperature = TemperatureReading.objects.all().order_by('read_at')

        # User might want to sort things backwards.
        if frontend_settings.reverse_dashboard_graphs:
            electricity = electricity.reverse()[:self.electricity_max]
            gas = gas.reverse()[:self.gas_max]
            temperature = temperature.reverse()[:self.temperature_max]
        else:
            # We can't slice using negative offsets, so we should fetch a (quick) count first)
            electricity_offset = max(0, electricity.count() - self.electricity_max)
            gas_offset = max(0, gas.count() - self.gas_max)
            temperature_offset = max(0, temperature.count() - self.temperature_max)

            electricity = electricity[electricity_offset:]
            gas = gas[gas_offset:]
            temperature = temperature[temperature_offset:]

        context_data['electricity_x'] = json.dumps(
            [x.read_at.astimezone(
                settings.LOCAL_TIME_ZONE
            ).strftime("%a %H:%M") for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )

        context_data['gas_x'] = json.dumps(
            [x.read_at.astimezone(
                settings.LOCAL_TIME_ZONE
            ).strftime("%a %H:%M") for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )

        context_data['track_temperature'] = WeatherSettings.get_solo().track

        if context_data['track_temperature']:
            context_data['temperature_x'] = json.dumps(
                [x.read_at.astimezone(
                    settings.LOCAL_TIME_ZONE
                ).strftime("%a %H:%M") for x in temperature]
            )
            context_data['temperature_y'] = json.dumps(
                [float(x.degrees_celcius) for x in temperature]
            )

        latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        latest_gas = GasConsumption.objects.all().order_by('-read_at')[0]

        context_data['latest_electricity_read'] = latest_electricity.read_at
        context_data['latest_electricity'] = int(
            latest_electricity.currently_delivered * 1000
        )
        context_data['latest_electricity_returned'] = int(
            latest_electricity.currently_returned * 1000
        )

        context_data['latest_gas_read'] = latest_gas.read_at
        context_data['latest_gas'] = latest_gas.currently_delivered

        try:
            context_data['consumption'] = dsmr_consumption.services.day_consumption(
                day=latest_electricity.read_at.astimezone(settings.LOCAL_TIME_ZONE).date()
            )
        except LookupError:
            pass

        return context_data


class HistoryMixin(object):
    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()

        context_data = super(HistoryMixin, self).get_context_data(**kwargs)
        context_data['usage'] = []
        context_data['days_ago'] = frontend_settings.recent_history_weeks * 7
        context_data['track_temperature'] = WeatherSettings.get_solo().track
        context_data['chart'] = defaultdict(list)

        CONSUMPTION_FIELDS = (
            'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'gas',
            'electricity1_cost', 'electricity2_cost', 'gas_cost', 'average_temperature'
        )

        now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
        dates = (
            now - timezone.timedelta(days=n) for n in reversed(
                range(1, context_data['days_ago'] + 1)
            )
        )

        for current_day in dates:
            current_day = current_day.astimezone(settings.LOCAL_TIME_ZONE)

            try:
                day_stats = DayStatistics.objects.get(day=current_day)
            except DayStatistics.DoesNotExist:
                continue

            context_data['usage'].append(day_stats)
            context_data['chart']['days'].append(current_day.strftime("%a %d-%m"))

            for current_field in CONSUMPTION_FIELDS:
                context_data['chart'][current_field].append(float(
                    getattr(day_stats, current_field)
                ))

        for key, value in context_data['chart'].items():
            context_data['chart'][key] = json.dumps(value)

        return context_data


class StatisticsMixin(object):
    def get_context_data(self, **kwargs):
        context_data = super(StatisticsMixin, self).get_context_data(**kwargs)
        today = timezone.now().astimezone(settings.LOCAL_TIME_ZONE).date()
        context_data['latest_reading'] = DsmrReading.objects.all().order_by('-pk')[0]
        context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0]
        context_data['total_reading_count'] = DsmrReading.objects.count()

        avg_electricity_per_hour = dsmr_consumption.services.average_electricity_by_hour()
        context_data['avg_electricity_x'] = json.dumps(
            ['{}:00'.format(x['hour']) for x in avg_electricity_per_hour]
        )
        context_data['avg_electricity_y'] = json.dumps(
            [float(x['avg_delivered'] * 1000) for x in avg_electricity_per_hour]
        )
        context_data['average_electricity_by_hour'] = avg_electricity_per_hour

        try:
            context_data['energy_prices'] = EnergySupplierPrice.objects.by_date(today)
        except EnergySupplierPrice.DoesNotExist:
            pass

        return context_data
